"""
Base example of a service processor
"""

import logging
import datetime
# Configure logging
logging.basicConfig(level=logging.INFO)


# This is an example implementation of a processor class that is fired by crontab.
# This should be done in the child image
class LoggingServiceProcessor():  # pylint: disable=R0903
    """
    Service processor that logs messages
    """
    def __init__(self):
        pass

    def process(self):
        """Main processor loop"""
        logging.info("Cron processor execution started at %s ...",datetime.datetime.utcnow())


if __name__ == "__main__":
    cls = LoggingServiceProcessor()
    cls.process()
