"""
Service processor factory
"""
import importlib
from typing import Optional
import logging
from rococo.messaging import BaseServiceProcessor
from .config_factory import Config

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_service_processor(config: Config) -> Optional[BaseServiceProcessor]:
    """
    Dynamically imports the service processor
    """
    processor_module = config.get_env_var("PROCESSOR_MODULE")
    try:
        # Dynamically import the module
        module = importlib.import_module(processor_module)

        # Access the class from the imported module
        dynamic_class = getattr(module, config.processor_type)

        # Create an instance of the dynamic class with the specified parameters
        instance = dynamic_class(*config.service_constructor_params)
        return instance
    except ImportError as e:
        logging.error("Error: Module '%s' not found. Error: %s",processor_module,e)
    except AttributeError as e:
        logging.error("Error: Class '%s' not found in module '%s'. Error: %s",
                      config.processor_type,processor_module,e)
    return None
