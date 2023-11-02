from rococo.messaging.base import BaseServiceProcessor
from factories import get_message_adapter, get_service_processor
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)




if __name__ == '__main__':
    messaging_type = os.environ.get("MESSAGING_TYPE")
    try:
        logging_service_processor = get_service_processor()
        queue_name = os.environ.get('QUEUE_NAME')
        message_adapter = get_message_adapter()
        message_adapter.consume_messages(queue_name=queue_name,callback_function=logging_service_processor.process)
    except Exception:
        logging.error(traceback.format_exc())
