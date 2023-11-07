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
        service_processor = get_service_processor(config)
        message_adapter = get_message_adapter(config)
        if config.messaging_type == "RabbitMqConnection":
            queue_name = os.environ.get('RABBITMQ_QUEUE')
            message_adapter.consume_messages(queue_name=queue_name,callback_function=service_processor.process,num_threads=config.num_threads)
        else:
            logging.error("Invalid config.messaging_type %s",config.messaging_type)
            
    except Exception: # pylint: disable=W0718
        logging.error(traceback.format_exc())
