"""
Processor for services
"""

import os
import sys
import logging
import traceback

from factories import get_message_adapter, get_service_processor
from utils import read_project_version, get_required_env

# Configure logging
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    try:
        # Get the current directory of the script
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the parent directory (project directory)
        parent_directory = os.path.dirname(current_directory)
        read_project_version(project_dir=parent_directory)
        if not get_required_env():
            raise ValueError("There was a problem reading .env file. Exiting program.")
    except ValueError:
        logging.error(traceback.format_exc())
        sys.exit()

    service_processor = get_service_processor()
    queue_name = os.environ.get('QUEUE_NAME')
    message_adapter = get_message_adapter()
    message_adapter.consume_messages(queue_name=queue_name,
                                        callback_function=service_processor.process)
