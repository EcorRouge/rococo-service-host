from dataclasses import dataclass


@dataclass(kw_only=True)
class ProcessorInfo:
    type: str
    queue_name: str
    version: str