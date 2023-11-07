"""
Service processor factory
"""

from rococo.messaging import BaseServiceProcessor
from .config_factory import Config

def get_service_processor(config:Config) -> BaseServiceProcessor:
    """
    Dynamically imports the service processor
    """
    try:
        # Dynamically import the module
        module = __import__("service_processors.service_processors")

        # Access the class from the imported module
        dynamic_class = getattr(module,config.processor_type)

        # Create an instance of the dynamic class with the specified parameters
        instance = dynamic_class(*config.service_constructor_params)
        return instance
    except ImportError:
        print("Error: Module 'service_processors.service_processors' not found.")
    except AttributeError:
        print(f"Error: Class '{config.processor_type}' not found in module 'service_processors.service_processors'.")