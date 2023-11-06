import pika
import json
import os


def test_rabbitmq_send_message():
    # Establish a connection to RabbitMQ server

    credentials = pika.PlainCredentials(
        username=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD")
    )
    parameters = pika.ConnectionParameters(
        host=os.environ.get("HOST"),
        port=int(os.environ.get("PORT")),
        virtual_host=os.environ.get("RABBITMQ_VIRTUAL_HOST"),
        credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    # Declare a queue named 'test_queue'
    channel.queue_declare(queue=os.environ.get("QUEUE_NAME"), durable=True)

    # Publish a message to the queue
    channel.basic_publish(exchange='',
                          routing_key=os.environ.get("QUEUE_NAME"),
                          body=json.dumps({"message": "Hello, RabbitMQ!"}))

    print("Message sent to RabbitMQ.")

    # Close the connection
    connection.close()
