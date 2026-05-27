"""
Unit tests for process.py
"""
import unittest
from unittest.mock import MagicMock, patch, call
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


class TestProcessCronJobs(unittest.TestCase):
    """Test cases for _process_cron_jobs"""

    @patch('process.BlockingScheduler')
    def test_process_cron_jobs_calls_correct_methods(self, mock_scheduler_cls):
        """Test _process_cron_jobs adds jobs for the correct methods"""
        from process import _process_cron_jobs

        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler

        config = MagicMock()
        config.cron_jobs = [
            {"method": "process_daily", "run_at_startup": False, "cron_expressions": ["0 0 * * *"]},
            {"method": "process_heartbeat", "run_at_startup": False, "cron_time_amount": 30, "cron_time_unit": "seconds", "cron_run_at": None},
        ]
        processor = MagicMock()
        processor.process_daily = MagicMock()
        processor.process_heartbeat = MagicMock()

        _process_cron_jobs(config, processor)

        self.assertEqual(mock_scheduler.add_job.call_count, 2)
        mock_scheduler.start.assert_called_once()

    @patch('process.BlockingScheduler')
    def test_process_cron_jobs_run_at_startup(self, mock_scheduler_cls):
        """Test _process_cron_jobs runs methods at startup when configured"""
        from process import _process_cron_jobs

        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler

        config = MagicMock()
        config.cron_jobs = [
            {"method": "process", "run_at_startup": True, "cron_expressions": ["0 0 * * *"]},
        ]
        processor = MagicMock()

        _process_cron_jobs(config, processor)

        processor.process.assert_called_once()

    @patch('process.BlockingScheduler')
    def test_process_cron_jobs_missing_method_raises(self, mock_scheduler_cls):
        """Test _process_cron_jobs raises AttributeError for missing method"""
        from process import _process_cron_jobs

        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler

        config = MagicMock()
        config.cron_jobs = [
            {"method": "nonexistent_method", "run_at_startup": False, "cron_expressions": ["0 0 * * *"]},
        ]
        processor = MagicMock(spec=[])  # no attributes

        with self.assertRaises(AttributeError):
            _process_cron_jobs(config, processor)

    @patch('process.get_service_processor')
    @patch('process.Config')
    @patch('process._process_cron_jobs')
    def test_main_dispatches_to_cron_jobs(self, mock_process_cron_jobs, mock_config_cls, mock_get_processor):
        """Test main() dispatches to _process_cron_jobs when cron_jobs is non-empty"""
        from process import main

        config = MagicMock()
        config.get_env_var.return_value = "CRON"
        config.cron_jobs = [{"method": "process", "run_at_startup": False, "cron_expressions": ["0 0 * * *"]}]
        config.validate_env_vars.return_value = True
        config.load_toml = MagicMock()
        config.get_project_version.return_value = "1.0.0"
        mock_config_cls.return_value = config

        mock_processor = MagicMock()
        mock_get_processor.return_value = mock_processor

        main()

        mock_process_cron_jobs.assert_called_once_with(config, mock_processor)


if __name__ == '__main__':
    unittest.main()

