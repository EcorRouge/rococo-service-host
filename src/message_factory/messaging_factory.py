from rococo.messaging.rabbitmq import RabbitMqConnection
import os

def get_message_adapter():
    rabbitmq_host = os.environ.get('RABBITMQ_HOST',False)
    rabbitmq_port = os.environ.get('RABBITMQ_PORT')
    rabbitmq_username = os.environ.get('RABBITMQ_USERNAME')
    rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD')
    rabbitmq_virtual_host = os.environ.get('RABBITMQ_VIRTUAL_HOST','')

    rabbitAdapter = RabbitMqConnection(rabbitmq_host,rabbitmq_port,rabbitmq_username,rabbitmq_password,rabbitmq_virtual_host)
    rabbitAdapter.__enter__()
    return rabbitAdapter