"""
Unit tests for process.py
"""
import unittest
import sys
import os

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestProcess(unittest.TestCase):
    """Test cases for process.py"""

    def test_process_module_imports(self):
        """Test that process.py can be imported without errors"""
        try:
            import process
            success = True
        except Exception as e:
            print(f"Import failed: {e}")
            success = False
        
        self.assertTrue(success)

    def test_process_module_has_logger(self):
        """Test that process module initializes logger"""
        import process
        self.assertTrue(hasattr(process, 'logger'))
        self.assertIsNotNone(process.logger)

    def test_process_module_structure(self):
        """Test that process.py has expected structure"""
        import process
        import inspect
        
        # Get the source code
        source = inspect.getsource(process)
        
        # Verify key imports are present
        self.assertIn('from logger import Logger', source)
        self.assertIn('import traceback', source)
        self.assertIn('from time import sleep', source)
        self.assertIn('import schedule', source)
        self.assertIn('from apscheduler.schedulers.blocking import BlockingScheduler', source)
        self.assertIn('from apscheduler.triggers.cron import CronTrigger', source)
        self.assertIn('from factories import get_message_adapter, get_service_processor', source)
        self.assertIn('from factories import Config', source)


if __name__ == '__main__':
    unittest.main()

