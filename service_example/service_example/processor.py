"""
Base example of a service processor within the child image
"""

# If PyCharm warns that logger is unresolved, this is because it resolves rococo_svchost as a directory.
# To resolve this, mark rococo_svchost dir as a SourcesRoot (right-click -> Mark directory as), then restart PyCharm.
from rococo_svchost.logger import Logger
from rococo.messaging import BaseServiceProcessor

# Configure logging

logger = Logger().get_logger()


# This is an example implementation of a BaseServiceProcessor class.
# This should be done in the child image
class ChildLoggingServiceProcessor(BaseServiceProcessor):  # pylint: disable=R0903
    """
    Service processor that logs messages
    """

    def process(self, message):
        logger.info("Received message: %s to the child image!", message)

    def __init__(self):
        super().__init__()
