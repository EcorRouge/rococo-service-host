"""
Base example of a service processor
"""

from logger import Logger
from rococo.messaging import BaseServiceProcessor

# Configure logging
logger = Logger().get_logger()


# This is an example implementation of a BaseServiceProcessor class.
# This should be done in the child image
class LoggingServiceProcessor(BaseServiceProcessor):  # pylint: disable=R0903
    """
    Service processor that logs messages
    """

    def process(self, message):
        logger.info("Received message: %s", message)

    def __init__(self):
        super().__init__()
