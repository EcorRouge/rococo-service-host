"""
Unit tests for config_factory.py
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from factories.config_factory import Config


class TestConfigFactory(unittest.TestCase):
    """Test cases for Config class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = Config()

    def _mock_env_var(self, env_dict):
        """Helper to mock get_env_var method"""
        def get_env_var_side_effect(key):
            return env_dict.get(key)
        return get_env_var_side_effect

    def test_validate_messaging_and_execution_type_valid_rabbitmq(self):
        """Test valid RabbitMQ messaging type"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_messaging_and_execution_type()
        self.assertTrue(result)

    def test_validate_messaging_and_execution_type_valid_sqs(self):
        """Test valid SQS messaging type"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'SqsConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_messaging_and_execution_type()
        self.assertTrue(result)

    def test_validate_messaging_and_execution_type_invalid(self):
        """Test invalid messaging type"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'InvalidConnection'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_messaging_and_execution_type()
        self.assertFalse(result)

    def test_validate_messaging_and_execution_type_cron(self):
        """Test CRON execution type bypasses messaging validation"""
        env_vars = {
            'EXECUTION_TYPE': 'CRON',
            'MESSAGING_TYPE': 'anything'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_messaging_and_execution_type()
        self.assertTrue(result)

    def test_validate_processor_config_valid(self):
        """Test valid processor configuration"""
        env_vars = {
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_processor_config()
        self.assertTrue(result)

    def test_validate_processor_config_missing_type(self):
        """Test missing PROCESSOR_TYPE"""
        env_vars = {
            'PROCESSOR_MODULE': 'test.module'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_processor_config()
        self.assertFalse(result)

    def test_validate_processor_config_missing_module(self):
        """Test missing PROCESSOR_MODULE"""
        env_vars = {
            'PROCESSOR_TYPE': 'TestProcessor'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_processor_config()
        self.assertFalse(result)

    def test_validate_cron_expressions_valid(self):
        """Test valid cron expressions"""
        env_vars = {
            'CRON_EXPRESSIONS': '0 0 * * *,0 12 * * *'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_expressions()
        self.assertTrue(result)
        self.assertEqual(len(self.config.cron_expressions), 2)

    def test_validate_cron_expressions_invalid(self):
        """Test invalid cron expression"""
        env_vars = {
            'CRON_EXPRESSIONS': 'invalid_cron'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_expressions()
        self.assertFalse(result)

    def test_validate_cron_time_amount_valid(self):
        """Test valid CRON_TIME_AMOUNT"""
        env_vars = {
            'CRON_TIME_AMOUNT': '5'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_amount()
        self.assertTrue(result)

    def test_validate_cron_time_amount_valid_float(self):
        """Test valid CRON_TIME_AMOUNT as float"""
        env_vars = {
            'CRON_TIME_AMOUNT': '5.5'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_amount()
        self.assertTrue(result)

    def test_validate_cron_time_amount_missing(self):
        """Test missing CRON_TIME_AMOUNT"""
        env_vars = {}
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_amount()
        self.assertFalse(result)

    def test_validate_cron_time_amount_invalid(self):
        """Test invalid CRON_TIME_AMOUNT"""
        env_vars = {
            'CRON_TIME_AMOUNT': 'not_a_number'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_amount()
        self.assertFalse(result)

    def test_validate_cron_time_unit_valid_seconds(self):
        """Test valid CRON_TIME_UNIT: seconds"""
        env_vars = {
            'CRON_TIME_UNIT': 'seconds'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_unit()
        self.assertTrue(result)

    def test_validate_cron_time_unit_valid_case_insensitive(self):
        """Test valid CRON_TIME_UNIT: case insensitive"""
        env_vars = {
            'CRON_TIME_UNIT': 'MINUTES'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_unit()
        self.assertTrue(result)

    def test_validate_cron_time_unit_valid_hours(self):
        """Test valid CRON_TIME_UNIT: hours"""
        env_vars = {
            'CRON_TIME_UNIT': 'hours'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_unit()
        self.assertTrue(result)

    def test_validate_cron_time_unit_valid_days(self):
        """Test valid CRON_TIME_UNIT: days"""
        env_vars = {
            'CRON_TIME_UNIT': 'days'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_unit()
        self.assertTrue(result)

    def test_validate_cron_time_unit_valid_weeks(self):
        """Test valid CRON_TIME_UNIT: weeks"""
        env_vars = {
            'CRON_TIME_UNIT': 'weeks'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_unit()
        self.assertTrue(result)

    def test_validate_cron_time_unit_invalid(self):
        """Test invalid CRON_TIME_UNIT"""
        env_vars = {
            'CRON_TIME_UNIT': 'invalid_unit'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_time_unit()
        self.assertFalse(result)

    def test_validate_cron_run_at_valid(self):
        """Test valid CRON_RUN_AT with days"""
        env_vars = {
            'CRON_RUN_AT': '10:00',
            'CRON_TIME_UNIT': 'days'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_run_at()
        self.assertTrue(result)

    def test_validate_cron_run_at_invalid_unit(self):
        """Test CRON_RUN_AT with invalid time unit"""
        env_vars = {
            'CRON_RUN_AT': '10:00',
            'CRON_TIME_UNIT': 'hours'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_run_at()
        self.assertFalse(result)

    def test_validate_cron_run_at_no_run_at(self):
        """Test CRON_RUN_AT when not specified"""
        env_vars = {
            'CRON_TIME_UNIT': 'days'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_run_at()
        self.assertTrue(result)

    def test_validate_run_at_startup_true(self):
        """Test RUN_AT_STARTUP set to true"""
        env_vars = {
            'RUN_AT_STARTUP': 'true'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._validate_run_at_startup()
        self.assertTrue(self.config.run_at_startup)

    def test_validate_run_at_startup_true_uppercase(self):
        """Test RUN_AT_STARTUP set to TRUE (case insensitive)"""
        env_vars = {
            'RUN_AT_STARTUP': 'TRUE'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._validate_run_at_startup()
        self.assertTrue(self.config.run_at_startup)

    def test_validate_run_at_startup_false(self):
        """Test RUN_AT_STARTUP set to false"""
        env_vars = {
            'RUN_AT_STARTUP': 'false'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._validate_run_at_startup()
        self.assertFalse(self.config.run_at_startup)

    def test_validate_run_at_startup_not_set(self):
        """Test RUN_AT_STARTUP when not set"""
        env_vars = {}
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._validate_run_at_startup()
        self.assertFalse(self.config.run_at_startup)

    def test_validate_cron_convenience_fields_valid(self):
        """Test valid cron convenience fields"""
        env_vars = {
            'CRON_TIME_AMOUNT': '5',
            'CRON_TIME_UNIT': 'minutes',
            'CRON_RUN_AT': '',
            'RUN_AT_STARTUP': 'false'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_convenience_fields()
        self.assertTrue(result)

    def test_validate_cron_convenience_fields_invalid_amount(self):
        """Test invalid CRON_TIME_AMOUNT in convenience fields"""
        env_vars = {
            'CRON_TIME_AMOUNT': 'invalid',
            'CRON_TIME_UNIT': 'minutes'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_convenience_fields()
        self.assertFalse(result)

    def test_validate_cron_convenience_fields_invalid_unit(self):
        """Test invalid CRON_TIME_UNIT in convenience fields"""
        env_vars = {
            'CRON_TIME_AMOUNT': '5',
            'CRON_TIME_UNIT': 'invalid'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_convenience_fields()
        self.assertFalse(result)

    def test_validate_cron_convenience_fields_invalid_run_at(self):
        """Test invalid CRON_RUN_AT configuration"""
        env_vars = {
            'CRON_TIME_AMOUNT': '5',
            'CRON_TIME_UNIT': 'hours',
            'CRON_RUN_AT': '10:00'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_convenience_fields()
        self.assertFalse(result)

    def test_validate_cron_config_not_cron(self):
        """Test cron validation when execution type is not CRON"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_config()
        self.assertTrue(result)

    def test_validate_cron_config_with_expressions(self):
        """Test cron validation with expressions"""
        env_vars = {
            'EXECUTION_TYPE': 'CRON',
            'CRON_EXPRESSIONS': '0 0 * * *'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_config()
        self.assertTrue(result)

    def test_validate_cron_config_with_convenience(self):
        """Test cron validation with convenience fields"""
        env_vars = {
            'EXECUTION_TYPE': 'CRON',
            'CRON_TIME_AMOUNT': '5',
            'CRON_TIME_UNIT': 'minutes'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_config()
        self.assertTrue(result)

    def test_setup_rabbitmq_params_basic(self):
        """Test RabbitMQ parameters setup"""
        env_vars = {
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_rabbitmq_params()
        self.assertTrue(result)
        self.assertEqual(len(self.config.messaging_constructor_params), 6)
        self.assertEqual(self.config.messaging_constructor_params[0], 'localhost')
        self.assertEqual(self.config.messaging_constructor_params[1], 5672)

    def test_setup_rabbitmq_params_with_threads(self):
        """Test RabbitMQ parameters setup with num threads"""
        env_vars = {
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config',
            'RABBITMQ_NUM_THREADS': '10'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_rabbitmq_params()
        self.assertTrue(result)
        self.assertEqual(self.config.num_threads, 10)

    def test_setup_rabbitmq_params_invalid_threads(self):
        """Test RabbitMQ parameters setup with invalid num threads"""
        env_vars = {
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config',
            'RABBITMQ_NUM_THREADS': 'invalid'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_rabbitmq_params()
        self.assertFalse(result)

    def test_setup_sqs_params_with_secret_access_key(self):
        """Test SQS parameters setup with AWS_SECRET_ACCESS_KEY"""
        env_vars = {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret',
            'AWS_REGION': 'us-east-1',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._setup_sqs_params()
        self.assertEqual(len(self.config.messaging_constructor_params), 4)
        self.assertEqual(self.config.messaging_constructor_params[0], 'test_key')
        self.assertEqual(self.config.messaging_constructor_params[1], 'test_secret')
        self.assertEqual(self.config.messaging_constructor_params[2], 'us-east-1')

    def test_setup_sqs_params_with_access_key_secret(self):
        """Test SQS parameters setup with AWS_ACCESS_KEY_SECRET"""
        env_vars = {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_ACCESS_KEY_SECRET': 'test_secret_alt',
            'AWS_REGION': 'us-west-2',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._setup_sqs_params()
        self.assertEqual(self.config.messaging_constructor_params[1], 'test_secret_alt')

    def test_setup_messaging_params_cron(self):
        """Test messaging params setup for CRON execution"""
        env_vars = {
            'EXECUTION_TYPE': 'CRON'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_messaging_params()
        self.assertTrue(result)

    def test_setup_messaging_params_rabbitmq(self):
        """Test messaging params setup for RabbitMQ"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_messaging_params()
        self.assertTrue(result)
        self.assertEqual(self.config.messaging_type, 'RabbitMqConnection')

    def test_setup_messaging_params_sqs(self):
        """Test messaging params setup for SQS"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'SqsConnection',
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret',
            'AWS_REGION': 'us-east-1',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_messaging_params()
        self.assertTrue(result)
        self.assertEqual(self.config.messaging_type, 'SqsConnection')

    def test_setup_messaging_params_invalid(self):
        """Test messaging params setup with invalid type"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'InvalidType'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._setup_messaging_params()
        self.assertFalse(result)

    def test_validate_env_vars_complete_valid(self):
        """Test complete valid environment variable validation"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module',
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config.validate_env_vars()
        self.assertTrue(result)
        self.assertEqual(self.config.processor_type, 'TestProcessor')

    def test_validate_env_vars_invalid_messaging(self):
        """Test env vars validation with invalid messaging type"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'InvalidConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config.validate_env_vars()
        self.assertFalse(result)

    def test_validate_env_vars_missing_processor(self):
        """Test env vars validation with missing processor config"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_MODULE': 'test.module'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config.validate_env_vars()
        self.assertFalse(result)

    def test_validate_env_vars_invalid_cron(self):
        """Test env vars validation with invalid cron config"""
        env_vars = {
            'EXECUTION_TYPE': 'CRON',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module',
            'CRON_EXPRESSIONS': 'invalid_cron'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config.validate_env_vars()
        self.assertFalse(result)

    def test_validate_env_vars_invalid_messaging_params(self):
        """Test env vars validation with invalid messaging params"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module',
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config',
            'RABBITMQ_NUM_THREADS': 'invalid'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        try:
            result = self.config.validate_env_vars()
        except ValueError:
            result = False
        self.assertFalse(result)


    def test_cron_expressions_none_value(self):
        """Test CRON_EXPRESSIONS as None causes AttributeError"""
        env_vars = {
            'EXECUTION_TYPE': 'CRON',
            'CRON_EXPRESSIONS': None
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        with self.assertRaises(AttributeError):
            self.config._validate_cron_expressions()

    def test_cron_time_unit_none_value(self):
        """Test CRON_TIME_UNIT as None causes AttributeError"""
        env_vars = {
            'CRON_TIME_UNIT': None
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        with self.assertRaises(AttributeError):
            self.config._validate_cron_time_unit()

    def test_rabbitmq_port_non_numeric(self):
        """Test RABBITMQ_PORT with non-numeric string"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module',
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': 'abc',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        with self.assertRaises(ValueError):
            self.config._setup_rabbitmq_params()

    def test_rabbitmq_port_float_string(self):
        """Test RABBITMQ_PORT with float string"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module',
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': '5672.5',
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        with self.assertRaises(ValueError):
            self.config._setup_rabbitmq_params()

    def test_rabbitmq_port_none_value(self):
        """Test RABBITMQ_PORT as None"""
        env_vars = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RabbitMqConnection',
            'PROCESSOR_TYPE': 'TestProcessor',
            'PROCESSOR_MODULE': 'test.module',
            'RABBITMQ_HOST': 'localhost',
            'RABBITMQ_PORT': None,
            'RABBITMQ_USER': 'guest',
            'RABBITMQ_PASSWORD': 'guest',
            'RABBITMQ_VIRTUAL_HOST': '/',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        with self.assertRaises(TypeError):
            self.config._setup_rabbitmq_params()

    def test_messaging_type_case_insensitive(self):
        """Test MESSAGING_TYPE with different cases"""
        # Test lowercase
        env_vars_lower = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'rabbitmqconnection'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars_lower))
        result = self.config._validate_messaging_and_execution_type()
        self.assertFalse(result)  # Should fail due to case sensitivity

        # Test uppercase
        env_vars_upper = {
            'EXECUTION_TYPE': 'MESSAGE',
            'MESSAGING_TYPE': 'RABBITMQCONNECTION'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars_upper))
        result = self.config._validate_messaging_and_execution_type()
        self.assertFalse(result)  # Should fail due to case sensitivity

    def test_aws_secret_key_precedence(self):
        """Test AWS_ACCESS_KEY_SECRET takes precedence over AWS_SECRET_ACCESS_KEY"""
        env_vars = {
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_ACCESS_KEY_SECRET': 'secret_from_access_key',
            'AWS_SECRET_ACCESS_KEY': 'secret_from_secret_access',
            'AWS_REGION': 'us-east-1',
            'CONSUME_CONFIG_FILE_PATH': '/path/to/config'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        self.config._setup_sqs_params()
        # AWS_ACCESS_KEY_SECRET should take precedence
        self.assertEqual(self.config.messaging_constructor_params[1], 'secret_from_access_key')

    def test_cron_expressions_with_whitespace(self):
        """Test CRON_EXPRESSIONS with whitespace after comma"""
        env_vars = {
            'CRON_EXPRESSIONS': '0 0 * * *, 0 12 * * *'
        }
        self.config.get_env_var = MagicMock(side_effect=self._mock_env_var(env_vars))
        result = self.config._validate_cron_expressions()
        self.assertTrue(result)
        # Check that expressions are parsed (may have leading/trailing whitespace)
        self.assertEqual(len(self.config.cron_expressions), 2)


if __name__ == '__main__':
    unittest.main()
