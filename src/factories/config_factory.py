"""
Host Config class
"""
from rococo.config import BaseConfig
from logger import Logger

logger = Logger().get_logger()


class Config(BaseConfig):
    """
    Host Config class
    """

    def __init__(self):
        super().__init__()
        self.messaging_type = None
        self.processor_type = None
        self.messaging_constructor_params = ()
        self.num_threads = 1
        self.cron_time = ""
        self.messaging_constructor_params = ()
        self.service_constructor_params = ()

    def validate_env_vars(self) -> bool:
        # keeping as list now as a placeholder for additional messaging services like SQS
        if (self.get_env_var("EXECUTION_TYPE")
            and self.get_env_var("EXECUTION_TYPE") not in ["CRON"]) and (
                self.get_env_var("MESSAGING_TYPE") not in ["RabbitMqConnection", "SqsConnection"]):
            logger.error("Invalid value for MESSAGING_TYPE env var %s",
                         self.get_env_var("MESSAGING_TYPE"))
            return False
        if self.get_env_var("PROCESSOR_TYPE") is None:
            logger.error("Invalid value for PROCESSOR_TYPE env var %s",
                         self.get_env_var("PROCESSOR_TYPE"))
            return False
        if self.get_env_var("PROCESSOR_MODULE") is None:
            logger.error("Invalid value for PROCESSOR_MODULE env var %s",
                         self.get_env_var("PROCESSOR_MODULE"))
            return False
        if self.get_env_var("EXECUTION_TYPE") == "CRON":
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
            valid_cron_units = ['seconds', 'minutes', 'hours', 'days', 'weeks']
            if self.get_env_var("CRON_TIME_UNIT").lower() not in valid_cron_units:
                logger.error("Invalid value for CRON_TIME_UNIT env var %s. Expected one of %s",
                             self.get_env_var("CRON_TIME_UNIT").lower(),
                             valid_cron_units)
                return False
            if self.get_env_var("CRON_RUN_AT") and self.get_env_var(
                    "CRON_TIME_UNIT").lower() != 'days':
                logger.error(
                    f"Invalid cron configuration. Provided CRON_RUN_AT of "
                    f"{self.get_env_var('CRON_RUN_AT')} while providing CRON_TIME_UNIT "
                    f"of {self.get_env_var('CRON_TIME_UNIT')}. Expected DAYS"
                )

        self.processor_type = self.get_env_var("PROCESSOR_TYPE")
        self.messaging_constructor_params = ()
        self.num_threads = 1

        if self.get_env_var("EXECUTION_TYPE") not in ["CRON"]:
            self.messaging_type = self.get_env_var("MESSAGING_TYPE")
            if self.messaging_type == "RabbitMqConnection":
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
                        self.num_threads = int(self.get_env_var("RABBITMQ_NUM_THREADS"))
                    except TypeError:
                        logger.error("Invalid value for RABBITMQ_NUM_THREADS %s . Expected int",
                                     self.get_env_var("RABBITMQ_NUM_THREADS"))
                        return False
            elif self.messaging_type == "SqsConnection":
                self.messaging_constructor_params = (
                    self.get_env_var('AWS_ACCESS_KEY_ID'),
                    self.get_env_var('AWS_ACCESS_KEY_SECRET') or self.get_env_var('AWS_SECRET_ACCESS_KEY'),
                    self.get_env_var('AWS_REGION')
                )
            else:
                logger.error("Invalid MESSAGING_TYPE %s", self.messaging_type)
                return False

        self.service_constructor_params = ()
        return True
