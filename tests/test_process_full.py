"""
Unit tests for process.py main execution flow
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import signal
import runpy

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from process import main

class TestProcessMain(unittest.TestCase):
    """Test cases for process.py main()"""

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.get_message_adapter')
    @patch('process.logger')
    def test_main_message_execution_rabbitmq(self, mock_logger, mock_get_adapter, mock_get_processor, mock_config_cls):
        """Test main execution with RabbitMQ message processor"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "MESSAGE",
            "MESSAGING_TYPE": "RabbitMqConnection",
            "PROCESSOR_TYPE": "TestProcessor",
            "QUEUE_NAME_PREFIX": "prefix_",
            "TestProcessor_QUEUE_NAME": "queue"
        }.get(key)
        mock_config.messaging_type = "RabbitMqConnection"
        
        mock_processor = MagicMock()
        mock_get_processor.return_value = mock_processor
        
        mock_adapter = MagicMock()
        mock_get_adapter.return_value.__enter__.return_value = mock_adapter
        
        # Execute
        main()
        
        # Verify
        mock_get_adapter.assert_called_once_with(mock_config)
        mock_adapter.consume_messages.assert_called_once_with(
            queue_name="prefix_queue",
            callback_function=mock_processor.process
        )

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.get_message_adapter')
    @patch('process.logger')
    def test_main_message_execution_invalid_messaging_type(self, mock_logger, mock_get_adapter, mock_get_processor, mock_config_cls):
        """Test main execution with invalid messaging type"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "MESSAGE",
            "MESSAGING_TYPE": "InvalidType"
        }.get(key)
        mock_config.messaging_type = "InvalidType"
        
        # Execute
        main()
        
        # Verify error logged
        mock_logger.error.assert_any_call("Invalid config.messaging_type %s", "InvalidType")

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.BlockingScheduler')
    @patch('process.CronTrigger')
    @patch('process.logger')
    def test_main_cron_expressions(self, mock_logger, mock_cron_trigger, mock_scheduler_cls, mock_get_processor, mock_config_cls):
        """Test main execution with CRON expressions"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.return_value = "CRON"
        mock_config.cron_expressions = ["* * * * *"]
        mock_config.run_at_startup = True
        
        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler
        
        mock_processor = MagicMock()
        mock_get_processor.return_value = mock_processor

        # Execute
        main()
        
        # Verify
        mock_scheduler_cls.assert_called_once()
        mock_cron_trigger.from_crontab.assert_called_with("* * * * *")
        mock_scheduler.add_job.assert_called()
        mock_scheduler.start.assert_called_once()
        # Verify run at startup
        mock_processor.process.assert_called()

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    @patch('process.logger')
    def test_main_simple_cron_seconds(self, mock_logger, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with simple cron (seconds)"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "seconds",
            "CRON_TIME_AMOUNT": "30"
        }.get(key)
        mock_config.cron_expressions = []
        mock_config.run_at_startup = False
        
        # Break infinite loop
        mock_sleep.side_effect = StopIteration
        
        # Execute
        try:
            main()
        except StopIteration:
            pass
        
        # Verify
        mock_schedule.every.assert_called_with(30.0)
        mock_schedule.every.return_value.seconds.do.assert_called()

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    @patch('process.logger')
    def test_main_simple_cron_days_run_at(self, mock_logger, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with simple cron (days) and RUN_AT"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "days",
            "CRON_TIME_AMOUNT": "1",
            "CRON_RUN_AT": "10:00"
        }.get(key)
        mock_config.cron_expressions = []
        
        # Break infinite loop
        mock_sleep.side_effect = StopIteration
        
        # Execute
        try:
            main()
        except StopIteration:
            pass
        
        # Verify
        mock_schedule.every.assert_called_with(1.0)
        mock_schedule.every.return_value.days.at.assert_called_with("10:00")

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.logger')
    def test_main_invalid_env_vars(self, mock_logger, mock_get_processor, mock_config_cls):
        """Test main execution with invalid env vars"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = False
        
        # Execute
        main()
        
        # Verify logic caught exception and logged it
        # The code raises ValueError, which is caught by except Exception
        mock_logger.error.assert_called()
        # Verify one of the calls was the exception we expect, or at least an error was logged

    @patch('process.Config')
    def test_main_keyboard_interrupt(self, mock_config_cls):
        """Test main execution handling KeyboardInterrupt"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.side_effect = KeyboardInterrupt
        
        # Execute - should pass silently
        main()


    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    def test_main_unsupported_cron_unit(self, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with unsupported cron unit"""
         # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "decades", # Invalid
            "CRON_TIME_AMOUNT": "1"
        }.get(key)
        mock_config.cron_expressions = []
        
        # Execute
        main()
        # Should catch exception and log error
        
    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    def test_main_simple_cron_branches(self, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test other simple cron branches (minutes, hours, weeks)"""
        units = ["minutes", "hours", "weeks"]
        
        for unit in units:
            mock_config = MagicMock()
            mock_config_cls.return_value = mock_config
            mock_config.validate_env_vars.return_value = True
            mock_config.get_env_var.side_effect = lambda key, u=unit: {
                "EXECUTION_TYPE": "CRON",
                "CRON_TIME_UNIT": u,
                "CRON_TIME_AMOUNT": "1",
                "CRON_RUN_AT": None
            }.get(key)
            mock_config.cron_expressions = []
            
            mock_sleep.side_effect = StopIteration
            
            try:
                main()
            except StopIteration:
                pass
            
            # Reset mocks for next loop
            mock_schedule.reset_mock()

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    def test_main_simple_cron_days_no_run_at(self, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test simple cron days without RUN_AT"""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "days",
            "CRON_TIME_AMOUNT": "1",
            "CRON_RUN_AT": None
        }.get(key)
        mock_config.cron_expressions = []
        
        mock_sleep.side_effect = StopIteration
        
        try:
            main()
        except StopIteration:
            pass
            
        mock_schedule.every.assert_called_with(1.0)
        mock_schedule.every.return_value.days.do.assert_called()
        
    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.get_message_adapter')
    @patch('process.logger')
    def test_main_load_toml_exception(self, mock_logger, mock_get_adapter, mock_get_processor, mock_config_cls):
        """Test main execution when load_toml raises exception"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        
        # Simulate load_toml failing
        mock_config.load_toml.side_effect = [Exception("File not foundUtils"), None] # Fail first time
        
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.return_value = "MESSAGE"
        mock_config.messaging_type = "RabbitMqConnection"
        
        # Execute
        main()
        
        # Verify execution continued
        mock_config.validate_env_vars.assert_called()
        # Verify first load_toml call caused exception which was caught (implied by execution continuing)

    def test_script_execution(self):
        """Test running process.py as a script"""
        import subprocess
        
        # Run with invalid environment to ensure it exits quickly
        env = os.environ.copy()
        # Ensure it fails validation
        env['EXECUTION_TYPE'] = 'INVALID' 
        
        # We expect it to exit with 0 (since check catches Exception and logs it) or 1?
        # The main() catches Exception, logs it. So it exits normally (code 0) generally, unless sys.exit(1) is called.
        # process.py doesn't call sys.exit(). It just ends function.
        # But if validate_env_vars returns False, it raises ValueError.
        # Caught by except Exception. Logs error. Function ends. Script ends.
        
        result = subprocess.run(
            [sys.executable, 'src/process.py'],
            env=env,
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True,
            text=True
        )
        
        # It should finish successfully (as in process didn't crash, it handled the error)
        self.assertEqual(result.returncode, 0)


    def test_if_name_main(self):
        """Test that main() is called when running as script using runpy"""
        # We need to run the module as __main__
        # This covers the if __name__ == "__main__": block
        
        file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'process.py')
        
        # This will execute the script. It might fail internally due to missing env vars,
        # but the main() function catches exceptions, so it should be fine.
        runpy.run_path(file_path, run_name='__main__')
        
    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.get_message_adapter')
    @patch('process.logger')
    def test_main_message_execution_sqs(self, mock_logger, mock_get_adapter, mock_get_processor, mock_config_cls):
        """Test main execution with SQS message processor"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "MESSAGE",
            "MESSAGING_TYPE": "SqsConnection",
            "PROCESSOR_TYPE": "TestProcessor",
            "QUEUE_NAME_PREFIX": "prefix_",
            "TestProcessor_QUEUE_NAME": "queue"
        }.get(key)
        mock_config.messaging_type = "SqsConnection"

        mock_processor = MagicMock()
        mock_get_processor.return_value = mock_processor

        mock_adapter = MagicMock()
        mock_get_adapter.return_value.__enter__.return_value = mock_adapter

        # Execute
        main()

        # Verify SQS path is executed
        mock_get_adapter.assert_called_once_with(mock_config)
        mock_adapter.consume_messages.assert_called_once_with(
            queue_name="prefix_queue",
            callback_function=mock_processor.process
        )

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.logger')
    def test_main_processor_returns_none(self, mock_logger, mock_get_processor, mock_config_cls):
        """Test main execution when get_service_processor returns None"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.return_value = "CRON"
        mock_config.cron_expressions = []
        mock_config.run_at_startup = True

        # Return None to simulate processor failure
        mock_get_processor.return_value = None

        # Execute - should catch AttributeError when trying to call None.process()
        main()

        # Verify error was logged
        mock_logger.error.assert_called()

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    @patch('process.logger')
    def test_main_cron_time_amount_non_numeric(self, mock_logger, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with non-numeric CRON_TIME_AMOUNT"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "seconds",
            "CRON_TIME_AMOUNT": "abc"  # Non-numeric
        }.get(key)
        mock_config.cron_expressions = []

        # Execute - should catch ValueError from float("abc")
        main()

        # Verify error was logged
        mock_logger.error.assert_called()

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    @patch('process.logger')
    def test_main_cron_time_amount_negative(self, mock_logger, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with negative CRON_TIME_AMOUNT"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "seconds",
            "CRON_TIME_AMOUNT": "-5"  # Negative number
        }.get(key)
        mock_config.cron_expressions = []

        mock_sleep.side_effect = StopIteration

        # Execute - negative values are technically valid floats
        try:
            main()
        except StopIteration:
            pass

        # Verify schedule was called with negative value (may cause runtime issues)
        mock_schedule.every.assert_called_with(-5.0)

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    @patch('process.logger')
    def test_main_cron_time_amount_scientific(self, mock_logger, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with scientific notation CRON_TIME_AMOUNT"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "seconds",
            "CRON_TIME_AMOUNT": "1e2"  # Scientific notation = 100
        }.get(key)
        mock_config.cron_expressions = []

        mock_sleep.side_effect = StopIteration

        # Execute
        try:
            main()
        except StopIteration:
            pass

        # Verify schedule was called with converted value (100.0)
        mock_schedule.every.assert_called_with(100.0)

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.schedule')
    @patch('process.sleep')
    @patch('process.logger')
    def test_main_cron_run_at_invalid_format(self, mock_logger, mock_sleep, mock_schedule, mock_get_processor, mock_config_cls):
        """Test main execution with invalid CRON_RUN_AT format"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.side_effect = lambda key: {
            "EXECUTION_TYPE": "CRON",
            "CRON_TIME_UNIT": "days",
            "CRON_TIME_AMOUNT": "1",
            "CRON_RUN_AT": "25:00"  # Invalid hour (>23)
        }.get(key)
        mock_config.cron_expressions = []

        # Mock the .at() method to raise exception for invalid time
        mock_at = MagicMock(side_effect=Exception("Invalid time format"))
        mock_schedule.every.return_value.days.at = mock_at

        # Execute - should catch exception from invalid time
        main()

        # Verify error was logged
        mock_logger.error.assert_called()

    @patch('process.Config')
    @patch('process.get_service_processor')
    @patch('process.BlockingScheduler')
    @patch('process.CronTrigger')
    @patch('process.logger')
    def test_main_multiple_cron_expressions(self, mock_logger, mock_cron_trigger, mock_scheduler_cls, mock_get_processor, mock_config_cls):
        """Test main execution with multiple cron expressions"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_config.validate_env_vars.return_value = True
        mock_config.get_env_var.return_value = "CRON"
        mock_config.cron_expressions = ["* * * * *", "*/5 * * * *"]
        mock_config.run_at_startup = False

        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler

        mock_processor = MagicMock()
        mock_get_processor.return_value = mock_processor

        # Execute
        main()

        # Verify both cron expressions were processed
        self.assertEqual(mock_cron_trigger.from_crontab.call_count, 2)
        self.assertEqual(mock_scheduler.add_job.call_count, 2)
        mock_cron_trigger.from_crontab.assert_any_call("* * * * *")
        mock_cron_trigger.from_crontab.assert_any_call("*/5 * * * *")
        mock_scheduler.start.assert_called_once()


if __name__ == '__main__':
    unittest.main()
