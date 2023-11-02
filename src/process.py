from rococo.messaging.base import BaseServiceProcessor
from processor_factory import get_message_adapter
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



if __name__ == '__main__':
    a_service_started = False
    messaging_type = os.environ.get("MESSAGING_TYPE")
    try:
        logging_service_processor = LoggingServiceProcessor()
        queue_name = os.environ.get('QUEUE_NAME')
        message_adapter = get_message_adapter()
        message_adapter.consume_messages(queue_name=queue_name,callback_function=logging_service_processor.process)
    except Exception:
        logging.error(traceback.format_exc())
