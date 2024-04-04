"""
Message adapter handling
"""

from rococo.messaging.base import MessageAdapter
from rococo.messaging.rabbitmq import RabbitMqConnection
from rococo.messaging.sqs import SqsConnection
from .config_factory import Config


def get_message_adapter(config: Config) -> MessageAdapter:
    """
    Returns a message adapter depending on MESSAGING_TYPE env var
    """
    if config.messaging_type == "RabbitMqConnection":
        adapter = RabbitMqConnection(*config.messaging_constructor_params)
        return adapter
    elif config.messaging_type == "SqsConnection":
        adapter = SqsConnection(*config.messaging_constructor_params)
        return adapter

    return MessageAdapter()
