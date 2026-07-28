"""
Host Config class
"""
import json
from rococo.config import BaseConfig
from logger import Logger

from apscheduler.triggers.cron import CronTrigger


logger = Logger().get_logger()


class Config(BaseConfig):
    """
    Host Config class
    """

    def __init__(self):
        super().__init__()
        self.messaging_type = None
        self.processor_type = None
        self.num_threads = 1
        self.cron_time = ""
        self.cron_expressions = []
        self.run_at_startup = False
        self.cron_jobs = []
        self.messaging_constructor_params = ()
        self.service_constructor_params = ()

        # Observability — provider-agnostic. Enabled implicitly based on
        # whether OBSERVABILITY_PROVIDER is set AND all env vars that
        # provider's own REQUIRED_CONFIG_KEYS declares are present.
        self.observability_enabled = False
        self.observability_provider = None
        self.observability_config = {}

    def _setup_observability_params(self):
        """
        Provider-agnostic observability setup. Reads OBSERVABILITY_PROVIDER
        to determine which provider class to use (see rococo.observability
        .PROVIDERS), then asks that class's own REQUIRED_CONFIG_KEYS for
        which env vars it needs — Config never hardcodes provider-specific
        env var names, so adding a new provider (Datadog, etc.) later
        requires zero changes here.
        """
        provider_name = self.get_env_var("OBSERVABILITY_PROVIDER")
        if not provider_name:
            logger.info("OBSERVABILITY_PROVIDER not set — observability disabled.")
            self.observability_enabled = False
            return

        try:
            from rococo.observability import get_observability_provider
        except ImportError:
            logger.warning(
                "OBSERVABILITY_PROVIDER=%s set but observability extras "
                "aren't installed — skipping.", provider_name
            )
            self.observability_enabled = False
            return

        try:
            provider_class = get_observability_provider(provider_name)
        except ValueError as e:
            logger.error(str(e))
            self.observability_enabled = False
            return

        required_keys = getattr(provider_class, "REQUIRED_CONFIG_KEYS", ())
        config = {key: self.get_env_var(key) for key in required_keys}

        missing = [key for key, value in config.items() if not value]
        if missing:
            logger.info(
                "Observability provider '%s' not enabled — missing env var(s): %s",
                provider_name, ", ".join(missing),
            )
            self.observability_enabled = False
            return

        # Common optional fields every provider reads off its own config dict,
        # layered on top of whatever provider-specific keys were collected
        # above. Names match the env vars the providers look up.
        config["SERVICE_NAME"] = self.get_env_var("SERVICE_NAME")
        config["APP_ENV"] = self.get_env_var("APP_ENV") or "production"

        if not config["SERVICE_NAME"]:
            logger.info(
                "Observability provider '%s' not enabled — SERVICE_NAME is required.",
                provider_name,
            )
            self.observability_enabled = False
            return

        self.observability_provider = provider_name
        self.observability_config = config
        self.observability_enabled = True
        logger.info(
            "Observability provider '%s' enabled for service_name=%s",
            provider_name, config["SERVICE_NAME"],
        )

    def _validate_messaging_and_execution_type(self) -> bool:
        """Validate MESSAGING_TYPE and EXECUTION_TYPE environment variables"""
        if (self.get_env_var("EXECUTION_TYPE")
            and self.get_env_var("EXECUTION_TYPE") not in ["CRON"]) and (
                self.get_env_var("MESSAGING_TYPE") not in ["RabbitMqConnection", "SqsConnection"]):
            logger.error("Invalid value for MESSAGING_TYPE env var %s",
                         self.get_env_var("MESSAGING_TYPE"))
            return False
        return True

    def _validate_processor_config(self) -> bool:
        """Validate PROCESSOR_TYPE and PROCESSOR_MODULE environment variables"""
        if self.get_env_var("PROCESSOR_TYPE") is None:
            logger.error("Invalid value for PROCESSOR_TYPE env var %s",
                         self.get_env_var("PROCESSOR_TYPE"))
            return False
        if self.get_env_var("PROCESSOR_MODULE") is None:
            logger.error("Invalid value for PROCESSOR_MODULE env var %s",
                         self.get_env_var("PROCESSOR_MODULE"))
            return False
        return True

    def _validate_cron_expressions(self) -> bool:
        """Validate CRON_EXPRESSIONS environment variable"""
        cron_expressions = self.get_env_var("CRON_EXPRESSIONS").split(",")
        for cron_expression in cron_expressions:
            try:
                CronTrigger.from_crontab(cron_expression)
                self.cron_expressions.append(cron_expression)
            except ValueError as e:
                logger.error("Invalid expression in CRON_EXPRESSIONS %s. Exception: %s",
                             cron_expression, e)
                return False
        logger.info("Using CRON_EXPRESSIONS: %s", cron_expressions)
        return True

    def _validate_cron_time_amount(self) -> bool:
        """Validate CRON_TIME_AMOUNT environment variable"""
        if self.get_env_var("CRON_TIME_AMOUNT") is None:
            logger.error("Invalid value for CRON_TIME_AMOUNT env var %s",
                         self.get_env_var("CRON_TIME_AMOUNT"))
            return False
        try:
            float(self.get_env_var("CRON_TIME_AMOUNT"))
        except Exception as e:  # pylint: disable=W0718
            logger.error("Exception %s. Invalid value for CRON_TIME_AMOUNT env var %s",
                         e,
                         self.get_env_var("CRON_TIME_AMOUNT"))
            return False
        return True

    def _validate_cron_time_unit(self) -> bool:
        """Validate CRON_TIME_UNIT environment variable"""
        valid_cron_units = ['seconds', 'minutes', 'hours', 'days', 'weeks']
        if self.get_env_var("CRON_TIME_UNIT").lower() not in valid_cron_units:
            logger.error("Invalid value for CRON_TIME_UNIT env var %s. Expected one of %s",
                         self.get_env_var("CRON_TIME_UNIT").lower(),
                         valid_cron_units)
            return False
        return True

    def _validate_cron_run_at(self) -> bool:
        """Validate CRON_RUN_AT configuration"""
        if self.get_env_var("CRON_RUN_AT") and self.get_env_var(
                "CRON_TIME_UNIT").lower() != 'days':
            logger.error(
                f"Invalid cron configuration. Provided CRON_RUN_AT of "
                f"{self.get_env_var('CRON_RUN_AT')} while providing CRON_TIME_UNIT "
                f"of {self.get_env_var('CRON_TIME_UNIT')}. Expected DAYS"
            )
            return False
        return True

    def _validate_run_at_startup(self):
        """Validate and set RUN_AT_STARTUP configuration"""
        if self.get_env_var("RUN_AT_STARTUP") is not None:
            run_at_startup = self.get_env_var("RUN_AT_STARTUP").lower()
            self.run_at_startup = bool(run_at_startup == "true")

    def _validate_cron_convenience_fields(self) -> bool:
        """Validate convenience CRON_* fields (TIME_AMOUNT, TIME_UNIT, RUN_AT)"""
        if not self._validate_cron_time_amount():
            return False
        if not self._validate_cron_time_unit():
            return False
        if not self._validate_cron_run_at():
            return False
        self._validate_run_at_startup()
        return True

    def _resolve_cron_jobs_raw(self):
        """Resolve the raw CRON_JOBS JSON string from env var or file."""
        inline = self.get_env_var("CRON_JOBS")
        if inline:
            return inline

        file_path = self.get_env_var("CRON_JOBS_FILE")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                logger.error("CRON_JOBS_FILE path does not exist: %s", file_path)
                return False
            except OSError as e:
                logger.error("Failed to read CRON_JOBS_FILE '%s': %s", file_path, e)
                return False

        return None

    def _validate_cron_jobs(self, raw: str) -> bool:
        """Validate CRON_JOBS JSON string (list of job definitions)"""
        try:
            jobs = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error("Invalid JSON in CRON_JOBS: %s", e)
            return False

        if not isinstance(jobs, list):
            logger.error("CRON_JOBS must be a JSON list")
            return False

        valid_cron_units = ['seconds', 'minutes', 'hours', 'days', 'weeks']
        validated_jobs = []

        for i, job in enumerate(jobs):
            has_expressions = "cron_expressions" in job
            has_simple = "cron_time_amount" in job or "cron_time_unit" in job

            if has_expressions and has_simple:
                logger.error("CRON_JOBS[%d]: cannot specify both cron_expressions and cron_time_amount/cron_time_unit", i)
                return False

            if not has_expressions and not has_simple:
                logger.error("CRON_JOBS[%d]: must specify either cron_expressions or cron_time_amount/cron_time_unit", i)
                return False

            method = job.get("method", "process")
            run_at_startup = job.get("run_at_startup", False)

            if has_expressions:
                expressions_str = job["cron_expressions"]
                expressions = [e.strip() for e in expressions_str.split(",")]
                for expr in expressions:
                    try:
                        CronTrigger.from_crontab(expr)
                    except ValueError as e:
                        logger.error("CRON_JOBS[%d]: invalid cron expression '%s': %s", i, expr, e)
                        return False
                validated_jobs.append({
                    "method": method,
                    "run_at_startup": run_at_startup,
                    "cron_expressions": expressions,
                })
            else:
                if "cron_time_amount" not in job or "cron_time_unit" not in job:
                    logger.error("CRON_JOBS[%d]: both cron_time_amount and cron_time_unit are required", i)
                    return False
                try:
                    amount = float(job["cron_time_amount"])
                except (ValueError, TypeError) as e:
                    logger.error("CRON_JOBS[%d]: invalid cron_time_amount: %s", i, e)
                    return False
                unit = str(job["cron_time_unit"]).lower()
                if unit not in valid_cron_units:
                    logger.error("CRON_JOBS[%d]: invalid cron_time_unit '%s'. Expected one of %s", i, unit, valid_cron_units)
                    return False
                cron_run_at = job.get("cron_run_at")
                if cron_run_at and unit != "days":
                    logger.error("CRON_JOBS[%d]: cron_run_at is only valid when cron_time_unit is 'days'", i)
                    return False
                validated_jobs.append({
                    "method": method,
                    "run_at_startup": run_at_startup,
                    "cron_time_amount": amount,
                    "cron_time_unit": unit,
                    "cron_run_at": cron_run_at,
                })

        self.cron_jobs = validated_jobs
        logger.info("Using CRON_JOBS: %s", validated_jobs)
        return True

    def _validate_cron_config(self) -> bool:
        """Validate CRON configuration"""
        if self.get_env_var("EXECUTION_TYPE") != "CRON":
            return True

        raw = self._resolve_cron_jobs_raw()
        if raw is False:
            return False
        if raw is not None:
            return self._validate_cron_jobs(raw)

        if self.get_env_var("CRON_EXPRESSIONS"):
            return self._validate_cron_expressions()
        else:
            return self._validate_cron_convenience_fields()

    def _setup_rabbitmq_params(self) -> bool:
        """Setup RabbitMQ connection parameters"""
        self.messaging_constructor_params = (
            self.get_env_var('RABBITMQ_HOST'),
            int(self.get_env_var('RABBITMQ_PORT')),
            self.get_env_var('RABBITMQ_USER'),
            self.get_env_var('RABBITMQ_PASSWORD'),
            self.get_env_var('RABBITMQ_VIRTUAL_HOST'),
            self.get_env_var('CONSUME_CONFIG_FILE_PATH')
        )
        if self.get_env_var("RABBITMQ_NUM_THREADS"):
            try:
                self.num_threads = int(
                    self.get_env_var("RABBITMQ_NUM_THREADS"))
            except (TypeError, ValueError):
                logger.error("Invalid value for RABBITMQ_NUM_THREADS %s . Expected int",
                             self.get_env_var("RABBITMQ_NUM_THREADS"))
                return False
        return True

    def _setup_sqs_params(self):
        """Setup SQS connection parameters"""
        self.messaging_constructor_params = (
            self.get_env_var('AWS_ACCESS_KEY_ID'),
            self.get_env_var('AWS_ACCESS_KEY_SECRET') or self.get_env_var(
                'AWS_SECRET_ACCESS_KEY'),
            self.get_env_var('AWS_REGION'),
            self.get_env_var('CONSUME_CONFIG_FILE_PATH')
        )

    def _setup_messaging_params(self) -> bool:
        """Setup messaging parameters based on messaging type"""
        if self.get_env_var("EXECUTION_TYPE") in ["CRON"]:
            return True

        self.messaging_type = self.get_env_var("MESSAGING_TYPE")
        if self.messaging_type == "RabbitMqConnection":
            return self._setup_rabbitmq_params()
        elif self.messaging_type == "SqsConnection":
            self._setup_sqs_params()
            return True
        else:
            logger.error("Invalid MESSAGING_TYPE %s", self.messaging_type)
            return False

    def validate_env_vars(self) -> bool:
        """Validate all environment variables and setup configuration"""
        if not self._validate_messaging_and_execution_type():
            return False
        if not self._validate_processor_config():
            return False
        if not self._validate_cron_config():
            return False

        self.processor_type = self.get_env_var("PROCESSOR_TYPE")
        self.messaging_constructor_params = ()
        self.num_threads = 1

        if not self._setup_messaging_params():
            return False

        self._setup_observability_params()

        self.service_constructor_params = ()
        return True
