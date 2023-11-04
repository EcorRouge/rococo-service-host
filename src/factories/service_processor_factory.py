from rococo.messaging import BaseServiceProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


# this will go elsewhere
class LoggingServiceProcessor(BaseServiceProcessor):

    def process(self, message):
        logging.info(f"Received message: {message}")

    def __init__(self):
        super().__init__()


def get_service_processor() -> BaseServiceProcessor:
    service_processor = BaseServiceProcessor()
    # hard coding for now
    if True:
        # if condition for LoggingServiceProcessor, then:
        service_processor = LoggingServiceProcessor()
    return service_processor
