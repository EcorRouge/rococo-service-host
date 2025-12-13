"""
Host Config class
"""
from rococo.config import BaseConfig
from logger import Logger

from apscheduler.triggers.cron import CronTrigger


logger = Logger().get_logger()


class Config(BaseConfig):
    """
    Host Config class
    """

    def __init__(self):
        super().__init__()
        self.messaging_type = None
        self.processor_type = None
        self.num_threads = 1
        self.cron_time = ""
        self.cron_expressions = []
        self.run_at_startup = False
        self.messaging_constructor_params = ()
        self.service_constructor_params = ()

    def _validate_messaging_and_execution_type(self) -> bool:
        """Validate MESSAGING_TYPE and EXECUTION_TYPE environment variables"""
        if (self.get_env_var("EXECUTION_TYPE")
            and self.get_env_var("EXECUTION_TYPE") not in ["CRON"]) and (
                self.get_env_var("MESSAGING_TYPE") not in ["RabbitMqConnection", "SqsConnection"]):
            logger.error("Invalid value for MESSAGING_TYPE env var %s",
                         self.get_env_var("MESSAGING_TYPE"))
            return False
        return True

    def _validate_processor_config(self) -> bool:
        """Validate PROCESSOR_TYPE and PROCESSOR_MODULE environment variables"""
        if self.get_env_var("PROCESSOR_TYPE") is None:
            logger.error("Invalid value for PROCESSOR_TYPE env var %s",
                         self.get_env_var("PROCESSOR_TYPE"))
            return False
        if self.get_env_var("PROCESSOR_MODULE") is None:
            logger.error("Invalid value for PROCESSOR_MODULE env var %s",
                         self.get_env_var("PROCESSOR_MODULE"))
            return False
        return True

    def _validate_cron_expressions(self) -> bool:
        """Validate CRON_EXPRESSIONS environment variable"""
        cron_expressions = self.get_env_var("CRON_EXPRESSIONS").split(",")
        for cron_expression in cron_expressions:
            try:
                CronTrigger.from_crontab(cron_expression)
                self.cron_expressions.append(cron_expression)
            except ValueError as e:
                logger.error("Invalid expression in CRON_EXPRESSIONS %s. Exception: %s",
                             cron_expression, e)
                return False
        logger.info("Using CRON_EXPRESSIONS: %s", cron_expressions)
        return True

    def _validate_cron_time_amount(self) -> bool:
        """Validate CRON_TIME_AMOUNT environment variable"""
        if self.get_env_var("CRON_TIME_AMOUNT") is None:
            logger.error("Invalid value for CRON_TIME_AMOUNT env var %s",
                         self.get_env_var("CRON_TIME_AMOUNT"))
            return False
        try:
            float(self.get_env_var("CRON_TIME_AMOUNT"))
        except Exception as e:  # pylint: disable=W0718
            logger.error("Exception %s. Invalid value for CRON_TIME_AMOUNT env var %s",
                         e,
                         self.get_env_var("CRON_TIME_AMOUNT"))
            return False
        return True

    def _validate_cron_time_unit(self) -> bool:
        """Validate CRON_TIME_UNIT environment variable"""
        valid_cron_units = ['seconds', 'minutes', 'hours', 'days', 'weeks']
        if self.get_env_var("CRON_TIME_UNIT").lower() not in valid_cron_units:
            logger.error("Invalid value for CRON_TIME_UNIT env var %s. Expected one of %s",
                         self.get_env_var("CRON_TIME_UNIT").lower(),
                         valid_cron_units)
            return False
        return True

    def _validate_cron_run_at(self) -> bool:
        """Validate CRON_RUN_AT configuration"""
        if self.get_env_var("CRON_RUN_AT") and self.get_env_var(
                "CRON_TIME_UNIT").lower() != 'days':
            logger.error(
                f"Invalid cron configuration. Provided CRON_RUN_AT of "
                f"{self.get_env_var('CRON_RUN_AT')} while providing CRON_TIME_UNIT "
                f"of {self.get_env_var('CRON_TIME_UNIT')}. Expected DAYS"
            )
            return False
        return True

    def _validate_run_at_startup(self):
        """Validate and set RUN_AT_STARTUP configuration"""
        if self.get_env_var("RUN_AT_STARTUP") is not None:
            run_at_startup = self.get_env_var("RUN_AT_STARTUP").lower()
            self.run_at_startup = bool(run_at_startup == "true")

    def _validate_cron_convenience_fields(self) -> bool:
        """Validate convenience CRON_* fields (TIME_AMOUNT, TIME_UNIT, RUN_AT)"""
        if not self._validate_cron_time_amount():
            return False
        if not self._validate_cron_time_unit():
            return False
        if not self._validate_cron_run_at():
            return False
        self._validate_run_at_startup()
        return True

    def _validate_cron_config(self) -> bool:
        """Validate CRON configuration"""
        if self.get_env_var("EXECUTION_TYPE") != "CRON":
            return True

        if self.get_env_var("CRON_EXPRESSIONS"):
            return self._validate_cron_expressions()
        else:
            return self._validate_cron_convenience_fields()

    def _setup_rabbitmq_params(self) -> bool:
        """Setup RabbitMQ connection parameters"""
        self.messaging_constructor_params = (
            self.get_env_var('RABBITMQ_HOST'),
            int(self.get_env_var('RABBITMQ_PORT')),
            self.get_env_var('RABBITMQ_USER'),
            self.get_env_var('RABBITMQ_PASSWORD'),
            self.get_env_var('RABBITMQ_VIRTUAL_HOST'),
            self.get_env_var('CONSUME_CONFIG_FILE_PATH')
        )
        if self.get_env_var("RABBITMQ_NUM_THREADS"):
            try:
                self.num_threads = int(
                    self.get_env_var("RABBITMQ_NUM_THREADS"))
            except (TypeError, ValueError):
                logger.error("Invalid value for RABBITMQ_NUM_THREADS %s . Expected int",
                             self.get_env_var("RABBITMQ_NUM_THREADS"))
                return False
        return True

    def _setup_sqs_params(self):
        """Setup SQS connection parameters"""
        self.messaging_constructor_params = (
            self.get_env_var('AWS_ACCESS_KEY_ID'),
            self.get_env_var('AWS_ACCESS_KEY_SECRET') or self.get_env_var(
                'AWS_SECRET_ACCESS_KEY'),
            self.get_env_var('AWS_REGION'),
            self.get_env_var('CONSUME_CONFIG_FILE_PATH')
        )

    def _setup_messaging_params(self) -> bool:
        """Setup messaging parameters based on messaging type"""
        if self.get_env_var("EXECUTION_TYPE") in ["CRON"]:
            return True

        self.messaging_type = self.get_env_var("MESSAGING_TYPE")
        if self.messaging_type == "RabbitMqConnection":
            return self._setup_rabbitmq_params()
        elif self.messaging_type == "SqsConnection":
            self._setup_sqs_params()
            return True
        else:
            logger.error("Invalid MESSAGING_TYPE %s", self.messaging_type)
            return False

    def validate_env_vars(self) -> bool:
        """Validate all environment variables and setup configuration"""
        if not self._validate_messaging_and_execution_type():
            return False
        if not self._validate_processor_config():
            return False
        if not self._validate_cron_config():
            return False

        self.processor_type = self.get_env_var("PROCESSOR_TYPE")
        self.messaging_constructor_params = ()
        self.num_threads = 1

        if not self._setup_messaging_params():
            return False

        self.service_constructor_params = ()
        return True
