import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class Config():
    def __init__(self):
        self.messaging_type = os.environ.get("MESSAGING_TYPE")
        self.processor_type = os.environ.get("PROCESSOR_TYPE")
        self.messaging_constructor_params = ()
        self.num_threads = 1
        if self.messaging_type == "RabbitMqConnection":
            self.messaging_constructor_params = (os.environ.get('RABBITMQ_HOST'),int(os.environ.get('RABBITMQ_PORT')),os.environ.get('RABBITMQ_DEFAULT_USER'),os.environ.get('RABBITMQ_DEFAULT_PASS'),os.environ.get('RABBITMQ_VIRTUAL_HOST', ''))
            self.num_threads = int(os.environ.get("RABBITMQ_NUM_THREADS",1))
        else:
            logging.error("Invalid MESSAGING_TYPE {}".format(self.messaging_type))
        self.service_constructor_params = ()

        

