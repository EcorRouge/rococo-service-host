from rococo.messaging.base import MessageAdapter
from rococo.messaging.rabbitmq import RabbitMqConnection
import os

def get_message_adapter() -> MessageAdapter:
    adapter = MessageAdapter()
    if os.environ.get("MESSAGING_TYPE") == "RABBITMQ":    
        host = os.environ.get('HOST')
        port = os.environ.get('PORT')
        username = os.environ.get('USERNAME')
        password = os.environ.get('PASSWORD')
        rabbitmq_virtual_host = os.environ.get('RABBITMQ_VIRTUAL_HOST','')

        adapter = RabbitMqConnection(host,port,username,password,rabbitmq_virtual_host)
    
    adapter.__enter__()
    return adapter