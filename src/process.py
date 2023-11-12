"""
Main loop for service processor host
"""
import os
import logging
import traceback
from src.factories import get_message_adapter, get_service_processor
from src.factories import Config

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
        config = Config()

        logging.info("Rococo Service Host Version:")
        config.load_toml("/app/src/info")
        
        # this will not output anything on the parent host
        logging.info("Service Processor Version:")
        config.load_toml("/app")

        if not config.validate_env_vars():
            raise ValueError("Invalid env configuration. Exiting program.")
        service_processor = get_service_processor(config)
        with get_message_adapter(config) as message_adapter:
            if config.messaging_type == "RabbitMqConnection":
                queue_name = config.get_env_var('RABBITMQ_QUEUE')
                message_adapter.consume_messages(queue_name=queue_name,
                                                callback_function=service_processor.process,
                                                num_threads=config.num_threads)
            else:
                logging.error("Invalid config.messaging_type %s",config.messaging_type)

    except Exception as e: # pylint: disable=W0718
        logging.error(traceback.format_exc())
        logging.error(e)
