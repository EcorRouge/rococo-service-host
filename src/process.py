from rococo.messaging.base import BaseServiceProcessor
import pika
import boto3
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)


class ServiceProcessor(BaseServiceProcessor):
    def __init__(self):
        pass

    def process(self,message):
        logging.info(f"Received message: {message}")

    def start_rabbit_mq_processor(self,rabbitmq_host,rabbitmq_queue_name):
        # RabbitMQ configuration
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_queue_name = rabbitmq_queue_name

        try:
            # Start listening to RabbitMQ
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(self.listen_rabbitmq)
        except KeyboardInterrupt:
            logging.info('Service interrupted. Exiting...')

    def start_sqs_processor(self,aws_access_key,aws_secret_key,aws_region,sqs_queue_url):
        # AWS SQS configuration
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.sqs_queue_url = sqs_queue_url
        try:
            # Start listening to SQS
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(self.listen_sqs)
        except Exception:
            logging.info('Service interrupted. Exiting...')

    def callback_rabbitmq(self,ch, method, properties, body):
        self.process(body)
        

    def callback_sqs(self,message):
        self.process(message.body)
        

    def listen_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
        channel = connection.channel()

        channel.queue_declare(queue=self.rabbitmq_queue_name)
        channel.basic_consume(queue=self.rabbitmq_queue_name, on_message_callback=self.callback_rabbitmq, auto_ack=True)

        logging.info('Waiting for messages from RabbitMQ.')
        channel.start_consuming()

    def listen_sqs(self):   
        sqs = boto3.resource('sqs', region_name=self.aws_region, aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key)
        queue = sqs.Queue(self.sqs_queue_url)

        logging.info('Waiting for messages from SQS.')
        while True:
            messages = queue.receive_messages(WaitTimeSeconds=20)
            for message in messages:
                self.callback_sqs(message)
                message.delete()



if __name__ == '__main__':

    import os
    
    try:
        rabbitmq_host = os.environ.get('RABBITMQ_HOST')
        rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE')
    except Exception as e:
        logging.error("One of the rabbitmq-service env vars was not found. Needs RABBITMQ_HOST, and RABBITMQ_QUEUE")
        logging.error(traceback.format_exc())

    try:
        aws_access_key = os.environ.get('AWS_ACCESS_KEY')
        aws_secret_key = os.environ.get('AWS_SECRET_KEY')
        aws_region = os.environ.get('AWS_REGION')
        sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
    except Exception:
        logging.error("One of the sqs-service env vars was not found. Needs AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, and SQS_QUEUE_URL")
        logging.error(traceback.format_exc())

    start_service = os.environ.get("START_SERVICE")

    a_service_started = False

    if start_service == "RABBITMQ":
        # Create instances of your ServiceProcessor class and use the configuration parameters
        try:
            rabbitmq_service_processor = ServiceProcessor()
            rabbitmq_service_processor.start_rabbit_mq_processor(rabbitmq_host, rabbitmq_queue)
            a_service_started = True
        except Exception:
            logging.error("Unexpected error when trying to initialize rabbitmq-service")
            logging.error(traceback.format_exc())

    if start_service == "SQS":
        # Create instances of your ServiceProcessor class and use the configuration parameters
        try:
            sqs_service_processor = ServiceProcessor()
            sqs_service_processor.start_sqs_processor(aws_access_key, aws_secret_key, aws_region, sqs_queue_url)
            a_service_started = True
        except Exception:
            logging.error("Unexpected error when trying to initialize sqs-service")
            logging.error(traceback.format_exc())

    if not a_service_started:
        logging.warning("No service was set to start.")