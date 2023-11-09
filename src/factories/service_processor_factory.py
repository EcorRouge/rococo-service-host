"""
Service processor factory
"""
from typing import Optional
from rococo.messaging import BaseServiceProcessor
from .config_factory import Config

def get_service_processor(config:Config) -> Optional[BaseServiceProcessor]:
    """
    Dynamically imports the service processor
    """
    try:
        # Dynamically import the module
        module = __import__(config.get_env_var("PROCESSOR_MODULE"))

        # Access the class from the imported module
        dynamic_class = getattr(module,config.processor_type)

        # Create an instance of the dynamic class with the specified parameters
        instance = dynamic_class(*config.service_constructor_params)
        return instance
    except ImportError:
        print("Error: Module '%s' not found.",config.get_env_var("PROCESSOR_MODULE"))
    except AttributeError:
        print("Error: Class '%s' not found in module '%s'.",
              config.processor_type,config.get_env_var("PROCESSOR_MODULE"))
    return None
