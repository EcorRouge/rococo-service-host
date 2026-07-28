"""
Unit tests for process.py
"""
import unittest
from unittest.mock import MagicMock, patch, call
from datetime import timedelta
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

    @patch('process.BlockingScheduler')
    def test_process_cron_jobs_run_at_uses_interval_trigger(self, mock_scheduler_cls):
        """Test _process_cron_jobs uses IntervalTrigger with correct days and start_date when cron_run_at is set"""
        from process import _process_cron_jobs
        from apscheduler.triggers.interval import IntervalTrigger

        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler

        config = MagicMock()
        config.cron_jobs = [
            {"method": "process", "run_at_startup": False, "cron_run_at": "02:00", "cron_time_amount": 3, "cron_time_unit": "days"},
        ]
        processor = MagicMock()

        _process_cron_jobs(config, processor)

        mock_scheduler.add_job.assert_called_once()
        trigger = mock_scheduler.add_job.call_args[0][1]
        self.assertIsInstance(trigger, IntervalTrigger)
        self.assertEqual(trigger.interval, timedelta(days=3))
        self.assertEqual(trigger.start_date.hour, 2)
        self.assertEqual(trigger.start_date.minute, 0)

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


class TestObservabilitySetup(unittest.TestCase):
    """Test cases for the observability wiring in process.py"""

    def _config(self, **overrides):
        config = MagicMock()
        config.observability_enabled = False
        config.observability_provider = None
        config.observability_config = {}
        config.cron_jobs = []
        for name, value in overrides.items():
            setattr(config, name, value)
        return config

    def test_disabled_returns_none(self):
        """Test no provider is built when observability is disabled"""
        from process import _maybe_get_observability
        self.assertIsNone(_maybe_get_observability(self._config()))

    def test_disabled_leaves_processor_untouched(self):
        """Test a service without observability config keeps its original methods"""
        from process import _setup_observability

        class Processor:
            def process(self):
                return "processed"

        processor = Processor()
        original = processor.process

        result = _setup_observability(self._config(), processor)

        self.assertIsNone(result)
        # Nothing was monkey-patched onto the instance
        self.assertNotIn("process", processor.__dict__)
        self.assertIs(processor.process.__func__, original.__func__)
        self.assertEqual(processor.process(), "processed")

    def test_provider_failure_does_not_raise(self):
        """Test a provider that fails to build is swallowed so the service still runs"""
        from process import _maybe_get_observability

        config = self._config(
            observability_enabled=True,
            observability_provider="open_observe",
            observability_config={},  # incomplete -> provider raises ValueError
        )
        self.assertIsNone(_maybe_get_observability(config))

    def test_setup_failure_does_not_raise(self):
        """Test any exception during observability setup is caught"""
        from process import _setup_observability

        observability = MagicMock()
        observability.get_logging_handler.side_effect = RuntimeError("boom")
        processor = MagicMock()

        with patch('process._maybe_get_observability', return_value=observability):
            result = _setup_observability(self._config(), processor)

        self.assertIsNone(result)

    def test_instrument_wraps_process_and_cron_job_methods(self):
        """Test tracing wraps 'process' plus every method named in cron_jobs"""
        from process import _instrument_service_processor

        class Processor:
            def process(self):
                return "process"

            def process_daily(self):
                return "daily"

        processor = Processor()
        config = self._config(cron_jobs=[
            {"method": "process_daily"},
            {"method": "missing_method"},
        ])
        observability = MagicMock()

        with patch('process._traced_callable', side_effect=lambda o, fn, name: fn) as mock_traced:
            _instrument_service_processor(processor, observability, config)

        span_names = sorted(call.args[2] for call in mock_traced.call_args_list)
        self.assertEqual(span_names, ["Processor.process", "Processor.process_daily"])

    def test_instrument_noop_when_observability_is_none(self):
        """Test the processor is left alone when there is no observability provider"""
        from process import _instrument_service_processor

        processor = MagicMock()
        with patch('process._traced_callable') as mock_traced:
            _instrument_service_processor(processor, None, self._config())
        mock_traced.assert_not_called()

    def test_traced_callable_records_exceptions_and_reraises(self):
        """Test the traced wrapper marks the span failed and lets the error propagate"""
        from process import _traced_callable

        def boom():
            raise ValueError("boom")

        observability = MagicMock()
        wrapped = _traced_callable(observability, boom, "Processor.process")

        with self.assertRaises(ValueError):
            wrapped()

    def test_traced_callable_returns_original_when_tracer_fails(self):
        """Test a failing tracer provider leaves the callable unwrapped"""
        from process import _traced_callable

        def work():
            return "worked"

        observability = MagicMock()
        observability.get_tracer_provider.side_effect = RuntimeError("no tracer")

        wrapped = _traced_callable(observability, work, "Processor.process")

        self.assertIs(wrapped, work)
        self.assertEqual(wrapped(), "worked")

    def test_traced_callable_preserves_return_value(self):
        """Test tracing does not change what the wrapped method returns"""
        from process import _traced_callable

        def work(value):
            return value * 2

        wrapped = _traced_callable(MagicMock(), work, "Processor.process")
        self.assertEqual(wrapped(21), 42)


if __name__ == '__main__':
    unittest.main()

