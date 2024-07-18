"""
Main loop for service processor host
"""

import importlib.metadata
import schedule
import traceback
from .factories import Config
from .factories import get_message_adapter, get_service_processor
from .logger import Logger
from os import path
from time import sleep

logger = Logger().get_logger()


def main():
    try:
        config = Config()

        svchost_package = path.basename(path.dirname(__file__))
        v = importlib.metadata.version(svchost_package)
        logger.info("Rococo Service Host Version: %s", v)

        if not config.validate_env_vars():
            raise ValueError("Invalid env configuration. Exiting program.")

        service_processor, processor_info = get_service_processor(config)
        logger.info("Service Processor Version: %s", processor_info.version)

        if config.get_env_var("EXECUTION_TYPE") not in ["CRON"]:  # if it's a message processor
            with get_message_adapter(config) as message_adapter:
                if config.messaging_type in ["RabbitMqConnection", "SqsConnection"]:
                    message_adapter.consume_messages(
                        queue_name=processor_info.queue_name,
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

    except KeyboardInterrupt:
        # Ignore KeyboardInterrupt
        pass

    except Exception as e:  # pylint: disable=W0718
        logger.error(traceback.format_exc())
        logger.error(e)


if __name__ == '__main__':
    main()