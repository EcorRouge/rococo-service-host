"""
Base example of a service processor
"""

import datetime
# If PyCharm warns that logger is unresolved, this is because it resolves rococo_svchost as a directory.
# To resolve this, mark rococo_svchost dir as a SourcesRoot (right-click -> Mark directory as), then restart PyCharm.
from rococo_svchost.logger import Logger

logger = Logger().get_logger()


# This is an example implementation of a processor class that is fired by crontab.
# This should be done in the child image
class LoggingServiceProcessor:  # pylint: disable=R0903
    """
    Service processor that logs messages
    """
    def __init__(self):
        pass

    def process(self):
        """Main processor loop"""
        logger.info("Cron processor execution started at %s ...", datetime.datetime.utcnow())
