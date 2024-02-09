"""
Main loop for service processor host
"""

from logger import Logger
import traceback
from time import sleep
import schedule
from factories import get_message_adapter, get_service_processor
from factories import Config

logger = Logger().get_logger()

if __name__ == '__main__':
    try:
        config = Config()
        try:
            config.load_toml("/app/src/info",log_version_string=False)
            logger.info("Rococo Service Host Version: %s",config.get_project_version())
        finally:
            pass

        config.project_version = ""
        config.load_toml("/app",log_version_string=False)
        logger.info("Service Processor Version: %s",config.get_project_version())

        if not config.validate_env_vars():
            raise ValueError("Invalid env configuration. Exiting program.")

        service_processor = get_service_processor(config)

        if config.get_env_var("EXECUTION_TYPE") not in ["CRON"]: # if its a message processor
            with get_message_adapter(config) as message_adapter:
                if config.messaging_type == "RabbitMqConnection":
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
        else: # if its cron
            # Schedule the job to run every 30 seconds
            unit = config.get_env_var("CRON_TIME_UNIT").lower()
            amount = float(config.get_env_var("CRON_TIME_AMOUNT"))
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

    except Exception as e:  # pylint: disable=W0718
        logger.error(traceback.format_exc())
        logger.error(e)
