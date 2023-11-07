"""
Message adapter handling
"""

from rococo.messaging.base import MessageAdapter
from rococo.messaging.rabbitmq import RabbitMqConnection
from .config_factory import Config

def get_message_adapter(config:Config) -> MessageAdapter:
    """
    Returns a message adapter depending on MESSAGING_TYPE env var
    """
    if config.messaging_type == "RabbitMqConnection":
        adapter = RabbitMqConnection(*config.messaging_constructor_params)
        adapter.__enter__()
        return adapter
    else:
        return MessageAdapter()
