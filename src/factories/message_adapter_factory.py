"""
Message adapter handling
"""

import os

from rococo.messaging.base import MessageAdapter
from rococo.messaging.rabbitmq import RabbitMqConnection

def get_message_adapter() -> MessageAdapter:
    """
    Returns a message adapter depending on MESSAGING_TYPE env var
    """
    if os.environ.get("MESSAGING_TYPE") == "RABBITMQ":
        host = os.environ.get('HOST')
        port = os.environ.get('PORT')
        username = os.environ.get('USERNAME')
        password = os.environ.get('PASSWORD')
        rabbitmq_virtual_host = os.environ.get('RABBITMQ_VIRTUAL_HOST','')
        with RabbitMqConnection(host, port, username, password, rabbitmq_virtual_host) as adapter:
            return adapter
    else:
        return MessageAdapter()
