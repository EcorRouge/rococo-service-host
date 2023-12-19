"""
Main loop for service processor host
"""

import logging
import traceback
from time import sleep
import sys
from crontab import CronTab
from factories import get_message_adapter, get_service_processor
from factories import Config

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
        config = Config()
        logging.info("Rococo Service Host Version:")
        try:
            config.load_toml("/app/src/info")
        finally:
            pass

        # this will not output anything on the parent host
        logging.info("Service Processor Version:")
        config.load_toml("/app")

        if not config.validate_env_vars():
            raise ValueError("Invalid env configuration. Exiting program.")
        
        if config.get_env_var("EXECUTION_TYPE") not in ["CRON"]: # if its a message processor
            service_processor = get_service_processor(config)
            with get_message_adapter(config) as message_adapter:
                if config.messaging_type == "RabbitMqConnection":
                    processor_class_name = config.get_env_var("PROCESSOR_TYPE")
                    queue_name = config.get_env_var(f'{processor_class_name}_QUEUE_NAME')+config.get_env_var("QUEUE_NAME_PREFIX")
                    message_adapter.consume_messages(
                        queue_name=queue_name,
                        callback_function=service_processor.process
                    )
                else:
                    logging.error("Invalid config.messaging_type %s", config.messaging_type)
        else: # if its cron
            cron = CronTab(user=True)
            # Create a new cron job
            job = cron.new(command=f"python /app/src/{config.get_env_var('PROCESSOR_MODULE').replace('.','/')}.py")
            job.setall(config.cron_time)

            # Write the cron job to the crontab
            cron.write()

            logging.info("Cron job created successfully. Keeping image alive.")
            try:
                while True:
                    sys.stdout.flush()
                    sleep(10)
            except KeyboardInterrupt:
                logging.info("Keyboard interrupt. Exiting gracefuly.")

    except Exception as e:  # pylint: disable=W0718
        logging.error(traceback.format_exc())
        logging.error(e)
