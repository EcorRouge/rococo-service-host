import os
from rococo.messaging import MessageAdapter, RabbitMqConnection


def get_message_adapter() -> MessageAdapter:
    adapter = MessageAdapter()
    if os.environ.get("MESSAGING_TYPE") == "RABBITMQ":
        host = os.environ.get('RABBITMQ_HOST')
        port: int = int(os.environ.get('RABBITMQ_PORT'))
        username = os.environ.get('RABBITMQ_DEFAULT_USER')
        password = os.environ.get('RABBITMQ_DEFAULT_PASS')
        rabbitmq_virtual_host = os.environ.get('RABBITMQ_VIRTUAL_HOST', '')

        adapter = RabbitMqConnection(host, port, username, password, rabbitmq_virtual_host)

    adapter.__enter__()
    return adapter
