"""
Service processor handling
"""

import logging

from rococo.messaging.base import BaseServiceProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)

# this will go elsewhere
# pylint: disable=too-few-public-methods
class LoggingServiceProcessor(BaseServiceProcessor):
    """
    Demo class based on BaseServiceProcessor
    """
    def __init__(self):
        pass

    def process(self,message):
        logging.info('Received message: %s', message)

def get_service_processor() -> BaseServiceProcessor:
    """
    Returns a service processor
    Hardcoded right now to return a LoggingServiceProcessor
    """
    return LoggingServiceProcessor()
