from rococo.messaging.base import BaseServiceProcessor
from rococo.messaging.rabbitmq import RabbitMqConnection
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# this will go elsewhere
class LoggingServiceProcessor(BaseServiceProcessor):
    def __init__(self):
        pass

    def process(self,message):
        logging.info(f"Received message: {message}")

def get_service_processor() -> BaseServiceProcessor:
    # hard coding for now
    service_processor = LoggingServiceProcessor()
    return service_processor