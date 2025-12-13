"""Logging module"""
import logging

class Logger:
    """Logging class"""
    _instance = None

    def __new__(cls):
        """Makes sure its a singleton to avoid duplicate logs."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        """Initialize logger"""
        # Create a custom logger
        if not hasattr(self, '_log_instance'):
            self._log_instance = logging.getLogger() # pylint: disable=W0201
            self._log_instance.setLevel(logging.INFO)

            # Create a formatter
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s')

            # Create a handler and set the formatter
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)

            # Add the handler to the logger
            self._log_instance.addHandler(handler)

    def get_logger(self):
        """Returns the initialized logger"""
        return self._log_instance