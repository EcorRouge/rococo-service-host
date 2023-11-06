import os

from rococo.messaging import BaseServiceProcessor
from service_processors.service_processors import LoggingServiceProcessor


def get_service_processor() -> BaseServiceProcessor:
    service_processor = BaseServiceProcessor()
    processor_type = os.environ.get("PROCESSOR_TYPE")
    if processor_type == "LoggingServiceProcessor":
        # if condition for LoggingServiceProcessor, then:
        service_processor = LoggingServiceProcessor()
    return service_processor
