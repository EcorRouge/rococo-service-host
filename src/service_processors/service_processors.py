import logging
from rococo.messaging import BaseServiceProcessor


# Configure logging
logging.basicConfig(level=logging.INFO)


# this will go elsewhere
class LoggingServiceProcessor(BaseServiceProcessor):

    def process(self, message):
        logging.info(f"Received message: {message}")

    def __init__(self):
        super().__init__()