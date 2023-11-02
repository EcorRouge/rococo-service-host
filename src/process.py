from rococo.messaging.base import BaseServiceProcessor
from message_factory import get_message_adapter
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)


class LoggingServiceProcessor(BaseServiceProcessor):
    def __init__(self):
        pass

    def process(self,message):
        logging.info(f"Received message: {message}")



def start_rabbit_mq_processor():
    logging_service_processor = LoggingServiceProcessor()
    rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE')
    rabbitmq_num_threads = int(os.environ.get('RABBITMQ_NUM_THREADS',1))

    rabbit_adapter = get_message_adapter()

    rabbit_adapter.consume_messages(queue_name=rabbitmq_queue,callback_function=logging_service_processor.process,num_threads=rabbitmq_num_threads)
    return

if __name__ == '__main__':
    try:
        start_rabbit_mq_processor()
        a_service_started = True
    except Exception:
        logging.error(traceback.format_exc())

    
    if not a_service_started:
        logging.warning("No service was set to start.")