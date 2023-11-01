from rococo.messaging.base import BaseServiceProcessor
from rococo.messaging.rabbitmq import RabbitMqConnection
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)


class LoggingServiceProcessor(BaseServiceProcessor):
    def __init__(self):
        pass

    def process(self,message):
        logging.info(f"Received message: {message}")



def start_rabbit_mq_processor(rabbitmq_host,rabbitmq_port,rabbitmq_username,rabbitmq_password,rabbitmq_queue_name,rabbitmq_virtual_host,rabbitmq_num_threads):
    logging_service_processor = LoggingServiceProcessor()
    rabbitAdapter = RabbitMqConnection(rabbitmq_host,rabbitmq_port,rabbitmq_username,rabbitmq_password,rabbitmq_virtual_host)
    rabbitAdapter.consume_messages(queue_name=rabbitmq_queue_name,callback_function=logging_service_processor.process,num_threads=rabbitmq_num_threads)
    return

if __name__ == '__main__':
    
    a_service_started = False


    try:
        rabbitmq_host = os.environ.get('RABBITMQ_HOST',False)
        if rabbitmq_host:
            rabbitmq_port = os.environ.get('RABBITMQ_PORT')
            rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE')
            rabbitmq_username = os.environ.get('RABBITMQ_USERNAME')
            rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD')
            rabbitmq_virtual_host = os.environ.get('RABBITMQ_VIRTUAL_HOST','')
            rabbitmq_num_threads = int(os.environ.get('RABBITMQ_NUM_THREADS',1))


            start_rabbit_mq_processor(rabbitmq_host=rabbitmq_host,rabbitmq_port=rabbitmq_port,rabbitmq_queue_name=rabbitmq_queue,rabbitmq_username=rabbitmq_username,rabbitmq_password=rabbitmq_password,rabbitmq_virtual_host=rabbitmq_virtual_host,rabbitmq_num_threads=rabbitmq_num_threads)

            a_service_started = True

    except Exception:
        logging.error(traceback.format_exc())

    
    if not a_service_started:
        logging.warning("No service was set to start.")