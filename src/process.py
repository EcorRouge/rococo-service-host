"""
Main loop for service processor host
"""

import logging
import traceback
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
        service_processor = get_service_processor(config)
        with get_message_adapter(config) as message_adapter:
            if config.messaging_type == "RabbitMqConnection":
                processor_class_name = config.get_env_var("PROCESSOR_TYPE")
                queue_name = config.get_env_var("QUEUE_NAME_PREFIX")+config.get_env_var(f'{processor_class_name}_QUEUE_NAME')
                message_adapter.consume_messages(
                    queue_name=queue_name,
                    callback_function=service_processor.process
                )
            else:
                logging.error("Invalid config.messaging_type %s", config.messaging_type)

    except Exception as e:  # pylint: disable=W0718
        logging.error(traceback.format_exc())
        logging.error(e)
