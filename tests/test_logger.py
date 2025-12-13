"""
Unit tests for logger.py
"""
import unittest
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logger import Logger


class TestLogger(unittest.TestCase):
    """Test cases for Logger class"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset the singleton instance before each test
        Logger._instance = None

    def test_logger_singleton(self):
        """Test that Logger is a singleton"""
        logger1 = Logger()
        logger2 = Logger()
        self.assertIs(logger1, logger2)

    def test_logger_initialization(self):
        """Test that logger initializes correctly"""
        logger = Logger()
        self.assertIsNotNone(logger)
        self.assertTrue(hasattr(logger, '_log_instance'))

    def test_get_logger(self):
        """Test get_logger returns a logging.Logger instance"""
        logger = Logger()
        log_instance = logger.get_logger()
        self.assertIsInstance(log_instance, logging.Logger)

    def test_logger_level(self):
        """Test that logger is set to INFO level"""
        logger = Logger()
        log_instance = logger.get_logger()
        self.assertEqual(log_instance.level, logging.INFO)

    def test_logger_has_handlers(self):
        """Test that logger has handlers attached"""
        logger = Logger()
        log_instance = logger.get_logger()
        self.assertGreater(len(log_instance.handlers), 0)

    def test_logger_handler_is_stream_handler(self):
        """Test that logger has a StreamHandler"""
        logger = Logger()
        log_instance = logger.get_logger()
        has_stream_handler = any(
            isinstance(handler, logging.StreamHandler)
            for handler in log_instance.handlers
        )
        self.assertTrue(has_stream_handler)

    def test_logger_handler_has_formatter(self):
        """Test that logger handlers have formatters"""
        logger = Logger()
        log_instance = logger.get_logger()
        for handler in log_instance.handlers:
            if isinstance(handler, logging.StreamHandler):
                self.assertIsNotNone(handler.formatter)

    def test_multiple_instantiation_no_duplicate_handlers(self):
        """Test that multiple instantiations don't create duplicate handlers"""
        logger1 = Logger()
        handler_count_1 = len(logger1.get_logger().handlers)
        
        logger2 = Logger()
        handler_count_2 = len(logger2.get_logger().handlers)
        
        # Handler count should remain the same due to singleton pattern
        self.assertEqual(handler_count_1, handler_count_2)

    def test_logger_can_log_messages(self):
        """Test that logger can actually log messages without errors"""
        logger = Logger()
        log_instance = logger.get_logger()
        
        # These should not raise any exceptions
        try:
            log_instance.info("Test info message")
            log_instance.error("Test error message")
            log_instance.warning("Test warning message")
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()

