from rococo.messaging.base import BaseServiceProcessor
import pika
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


class ServiceProcessor(BaseServiceProcessor):
    def __init__(self):
        pass

    def start_rabbit_mq_processor(self,rabbitmq_host,rabbitmq_queue_name):
        # RabbitMQ configuration
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_queue_name = rabbitmq_queue_name

        try:
            # Start listening to RabbitMQ and SQS simultaneously
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
            # Start listening to RabbitMQ and SQS simultaneously
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(self.listen_sqs)
        except KeyboardInterrupt:
            logging.info('Service interrupted. Exiting...')

    def callback_rabbitmq(ch, method, properties, body):
        logging.info(f"Received message from RabbitMQ: {body}")

    def callback_sqs(message):
        logging.info(f"Received message from SQS: {message.body}")

    def listen_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
        channel = connection.channel()

        channel.queue_declare(queue=self.rabbitmq_queue_name)
        channel.basic_consume(queue=self.rabbitmq_queue_name, on_message_callback=self.callback_rabbitmq, auto_ack=True)

        logging.info('Waiting for messages from RabbitMQ. To exit press CTRL+C')
        channel.start_consuming()

    def listen_sqs(self):   
        sqs = boto3.resource('sqs', region_name=self.aws_region, aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key)
        queue = sqs.Queue(self.sqs_queue_url)

        logging.info('Waiting for messages from SQS. To exit press CTRL+C')
        while True:
            messages = queue.receive_messages(WaitTimeSeconds=20)
            for message in messages:
                self.callback_sqs(message)
                message.delete()
