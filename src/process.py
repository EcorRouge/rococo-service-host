"""
Main loop for service processor host
"""

from logger import Logger
import traceback
from datetime import datetime, time, timedelta
from time import sleep
from functools import wraps
import schedule
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from factories import get_message_adapter, get_service_processor
from factories import Config

logger = Logger().get_logger()


def _maybe_get_observability(config):
    """
    Instantiates whichever observability provider was configured (if any).
    Returns None if observability isn't enabled, or if the extras for the
    configured provider aren't installed.
    """
    if not config.observability_enabled:
        return None
    try:
        from rococo.observability import get_observability_provider
    except ImportError:
        logger.warning("Observability enabled but extras aren't installed — skipping.")
        return None

    try:
        provider_class = get_observability_provider(config.observability_provider)
        return provider_class(**config.observability_config)
    except Exception:  # pylint: disable=W0718
        # Observability is never worth taking the service down for.
        logger.error(
            "Failed to initialize observability provider '%s' — continuing without it.\n%s",
            config.observability_provider, traceback.format_exc(),
        )
        return None


def _traced_callable(observability, callable_fn, span_name):
    """
    Wraps a single callable in a span, if tracing is available. Returns the
    callable untouched when the tracing extras are missing or the tracer
    provider can't be built, so a service is never broken by tracing.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode
    except ImportError:
        logger.warning("Tracing extras aren't installed — %s not instrumented.", span_name)
        return callable_fn

    try:
        observability.get_tracer_provider()   # registers once, no-ops if already done
    except Exception:  # pylint: disable=W0718
        logger.error(
            "Could not set up the tracer provider — %s not instrumented.\n%s",
            span_name, traceback.format_exc(),
        )
        return callable_fn

    tracer = trace.get_tracer(__name__)

    @wraps(callable_fn)
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(span_name) as span:
            try:
                return callable_fn(*args, **kwargs)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    return wrapper


def _instrument_service_processor(service_processor, observability, config):
    """
    Monkey-patches service_processor's own bound methods in place, once,
    at startup — so every _process_* dispatch function can keep calling
    service_processor.process (or whatever job method) completely
    unmodified, with no awareness that tracing exists at all.

    Wraps "process" (used by message consumption, simple cron, and cron
    expressions) plus every distinct method name referenced in
    config.cron_jobs (used by _process_cron_jobs, which can call methods
    other than "process").
    """
    if observability is None:
        return

    method_names = {"process"}
    for job in (config.cron_jobs or []):
        method_names.add(job.get("method", "process"))

    processor_class_name = service_processor.__class__.__name__

    for name in method_names:
        if not hasattr(service_processor, name):
            continue
        original = getattr(service_processor, name)
        span_name = f"{processor_class_name}.{name}"
        traced = _traced_callable(observability, original, span_name)
        setattr(service_processor, name, traced)
        logger.info("Instrumented %s with tracing", span_name)


def _setup_observability(config, service_processor):
    """
    Wires up logging + tracing for the configured provider, if any. Any
    failure is logged and swallowed — observability is strictly additive and
    must never stop the service from processing work.
    """
    try:
        observability = _maybe_get_observability(config)
        if observability is None:
            return None

        logger.addHandler(observability.get_logging_handler())
        try:
            from rococo.repositories.postgresql import PostgreSQLRepository
            observability.enable_class_tracing(PostgreSQLRepository)
        except ImportError:
            pass

        _instrument_service_processor(service_processor, observability, config)
        return observability
    except Exception:  # pylint: disable=W0718
        logger.error(
            "Observability setup failed — continuing without it.\n%s",
            traceback.format_exc(),
        )
        return None


def _process_messages(config, service_processor):
    with get_message_adapter(config) as message_adapter:
        if config.messaging_type in ["RabbitMqConnection", "SqsConnection"]:
            processor_class_name = config.get_env_var("PROCESSOR_TYPE")
            queue_name = config.get_env_var(
                "QUEUE_NAME_PREFIX")+config.get_env_var(
                    f'{processor_class_name}_QUEUE_NAME')
            message_adapter.consume_messages(
                queue_name=queue_name,
                callback_function=service_processor.process
            )
        else:
            logger.error("Invalid config.messaging_type %s", config.messaging_type)

def _process_cron_expressions(config, service_processor):
    scheduler = BlockingScheduler()
    for expression in config.cron_expressions:
        trigger = CronTrigger.from_crontab(expression)
        scheduler.add_job(service_processor.process, trigger)

    # Run at startup if configured
    if config.run_at_startup:
        logger.info("Running processor at startup as RUN_AT_STARTUP is set to true for cron with cron expressions")
        service_processor.process()

    scheduler.start()

def _process_cron_jobs(config, service_processor):
    scheduler = BlockingScheduler()
    for job in config.cron_jobs:
        method_name = job["method"]
        if not hasattr(service_processor, method_name):
            raise AttributeError(
                f"Processor {type(service_processor).__name__} has no method '{method_name}'"
            )
        callable_method = getattr(service_processor, method_name)

        if "cron_expressions" in job:
            for expression in job["cron_expressions"]:
                trigger = CronTrigger.from_crontab(expression)
                scheduler.add_job(callable_method, trigger)
        elif job.get("cron_run_at"):
            parts = job["cron_run_at"].split(":")
            hour, minute = int(parts[0]), int(parts[1])
            amount = job["cron_time_amount"]
            run_time = time(hour, minute)
            now = datetime.now()
            start_date = datetime.combine(now.date(), run_time)
            if start_date <= now:
                start_date += timedelta(days=1)
            trigger = IntervalTrigger(days=amount, start_date=start_date)
            scheduler.add_job(callable_method, trigger)
        else:
            unit = job["cron_time_unit"]
            amount = job["cron_time_amount"]
            trigger = IntervalTrigger(**{unit: amount})
            scheduler.add_job(callable_method, trigger)

        if job["run_at_startup"]:
            logger.info("Running %s at startup", method_name)
            callable_method()

    scheduler.start()

def _process_simple_cron(config, service_processor):
    unit = config.get_env_var("CRON_TIME_UNIT").lower()
    amount = float(config.get_env_var("CRON_TIME_AMOUNT"))

    # Run at startup if configured
    if config.run_at_startup:
        logger.info("Running processor at startup as RUN_AT_STARTUP is set to true for simple cron")
        service_processor.process()

    if unit == "seconds":
        schedule.every(amount).seconds.do(service_processor.process)
    elif unit == "minutes":
        schedule.every(amount).minutes.do(service_processor.process)
    elif unit == "hours":
        schedule.every(amount).hours.do(service_processor.process)
    elif unit == "days":
        if config.get_env_var("CRON_RUN_AT"):
            schedule.every(amount).days.at(
                config.get_env_var("CRON_RUN_AT")).do(service_processor.process)
        else:
            schedule.every(amount).days.do(service_processor.process)
    elif unit == "weeks":
        schedule.every(amount).weeks.do(service_processor.process)
    else:
        raise ValueError(f"Unsupported time unit {unit}")

    while True:
        schedule.run_pending()
        sleep(1)

def main():
    try:
        config = Config()
        try:
            config.load_toml("/app/src/info",log_version_string=False)
            logger.info("Rococo Service Host Version: %s",config.get_project_version())
        except Exception:  # pylint: disable=W0718
            # Version info is optional, continue without it
            pass

        config.project_version = ""
        config.load_toml("/app",log_version_string=False)
        logger.info("Service Processor Version: %s",config.get_project_version())

        if not config.validate_env_vars():
            raise ValueError("Invalid env configuration. Exiting program.")

        service_processor = get_service_processor(config)

        # Observability — set up once, here. If enabled, this patches
        # service_processor's own methods in place. Failures here are logged
        # and swallowed: a service must still run without observability.
        _setup_observability(config, service_processor)

        if config.get_env_var("EXECUTION_TYPE") not in ["CRON"]: # if its a message processor
            _process_messages(config, service_processor)
        elif config.cron_jobs:  # if its cron with multiple jobs
            _process_cron_jobs(config, service_processor)
        elif config.cron_expressions:  # if its cron with cron expressions
            _process_cron_expressions(config, service_processor)
        else: # if its simple cron
            _process_simple_cron(config, service_processor)

    except KeyboardInterrupt:
        # Ignore KeyboardInterrupt
        pass

    except Exception as e:  # pylint: disable=W0718
        logger.error(traceback.format_exc())
        logger.error(e)


if __name__ == '__main__':
    main()
