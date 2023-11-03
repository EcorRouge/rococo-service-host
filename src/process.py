from factories import get_message_adapter, get_service_processor
from utils import read_project_version, get_required_env
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    try:
        read_project_version(project_dir=os.path.dirname(os.path.abspath(__file__)))
        if not get_required_env():
            raise Exception("There was a problem reading .env file. Exiting program.")

        service_processor = get_service_processor()
        queue_name = os.environ.get('QUEUE_NAME')
        message_adapter = get_message_adapter()
        message_adapter.consume_messages(queue_name=queue_name,callback_function=service_processor.process)
    except Exception:
        logging.error(traceback.format_exc())
