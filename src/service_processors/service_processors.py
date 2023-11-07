"""
Base example of a service processor
"""

import logging
from rococo.messaging import BaseServiceProcessor


# Configure logging
logging.basicConfig(level=logging.INFO)


# this will go elsewhere
class LoggingServiceProcessor(BaseServiceProcessor):
    """
    Service processor that logs messages
    """
    def process(self, message):
        logging.info("Received message: %s",message)

    def __init__(self):
        pass