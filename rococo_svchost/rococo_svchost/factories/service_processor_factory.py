"""
Service processor factory
"""
import importlib
import importlib.metadata
import inspect
import subprocess
from ..logger import Logger
from ..models import ProcessorInfo
from .config_factory import Config
from glob import glob
from os import path
from rococo.messaging import BaseServiceProcessor
from typing import Optional, Tuple


logger = Logger().get_logger()


def get_service_processor(config: Config) -> Optional[Tuple[BaseServiceProcessor, ProcessorInfo]]:
    """
    Dynamically imports the service processor
    """
    result = subprocess.run("poetry version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout.strip().split(' ')
        processor_package = output[0].replace('-', '_')
        processor_module = find_processor_module(processor_package)
    else:
        processor_module = config.processor_module
        processor_package = processor_module.split('.')[0]

    logger.info(f"processor_module: {processor_module}")

    processor_type, dynamic_class = find_processor_type(processor_module)
    if processor_type is None:
        processor_type = config.processor_type

    logger.info(f"processor_type: {processor_type}")

    # Create an instance of the dynamic class with the specified parameters
    instance = dynamic_class(*config.service_constructor_params)

    queue_name_prefix = config.get_env_var("QUEUE_NAME_PREFIX")
    queue_name_base = config.get_env_var(f'{processor_type}_QUEUE_NAME')
    queue_name = queue_name_prefix + queue_name_base if queue_name_prefix and queue_name_base else None

    return instance, ProcessorInfo(
        type=processor_type,
        queue_name=queue_name,
        version=importlib.metadata.version(processor_package))


def find_processor_module(processor_package: str) -> str:
    init_module = importlib.import_module(processor_package)
    search_root_dir = init_module.__path__[0]
    search_pattern = path.join(search_root_dir, "**", "processor.py")
    processor_path: str = glob(search_pattern, recursive=True)[0]

    if processor_path is not None:
        # e.g. /somedir/rococo_svchost/services/processor.py -> rococo_svchost.services.processor
        return (path.basename(search_root_dir)
                + processor_path.removeprefix(search_root_dir).removesuffix('.py').replace(path.sep, '.'))


def find_processor_type(processor_module: str):
    module = importlib.import_module(processor_module)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj is not BaseServiceProcessor and issubclass(obj, BaseServiceProcessor):
            return name, obj

    for name, obj in inspect.getmembers(module):
        if name.lower().endswith("serviceprocessor"):
            return name, obj

    return None, None
