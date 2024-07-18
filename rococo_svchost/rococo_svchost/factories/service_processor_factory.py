"""
Service processor factory
"""
import importlib
from typing import Optional
import traceback
from rococo.messaging import BaseServiceProcessor
from ..logger import Logger
from .config_factory import Config

logger = Logger().get_logger()


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
        logger.error("Error: Module '%s' not found. Error: %s",processor_module,e)
        logger.error(traceback.format_exc())
        logger.error(traceback.format_stack())
    except AttributeError as e:
        logger.error("Error: Class '%s' not found in module '%s'. Error: %s",
                      config.processor_type,processor_module,e)
        logger.error(traceback.format_exc())
        logger.error(traceback.format_stack())
    return None
