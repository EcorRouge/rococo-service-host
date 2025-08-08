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
            # If CRON_EXPRESSIONS is provided, use it and ignore other CRON_* fields
            if self.get_env_var("CRON_EXPRESSIONS"):
                cron_expressions = self.get_env_var(
                    "CRON_EXPRESSIONS").split(",")
                # Validate each expression in CRON_EXPRESSIONS
                for cron_expression in cron_expressions:
                    try:
                        CronTrigger.from_crontab(cron_expression)
                        self.cron_expressions.append(cron_expression)
                    except ValueError as e:
                        logger.error("Invalid expression in CRON_EXPRESSIONS %s. Exception: %s",
                                     cron_expression, e)
                        return False
                logger.info("Using CRON_EXPRESSIONS: %s", cron_expressions)
            else:
                # Otherwise, validate the convenience CRON_* fields
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
                valid_cron_units = ['seconds',
                                    'minutes', 'hours', 'days', 'weeks']
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

                # Validate RUN_AT_STARTUP if provided
                if self.get_env_var("RUN_AT_STARTUP") is not None:
                    run_at_startup = self.get_env_var("RUN_AT_STARTUP").lower()
                    self.run_at_startup = bool(run_at_startup == "true")

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
                        self.num_threads = int(
                            self.get_env_var("RABBITMQ_NUM_THREADS"))
                    except TypeError:
                        logger.error("Invalid value for RABBITMQ_NUM_THREADS %s . Expected int",
                                     self.get_env_var("RABBITMQ_NUM_THREADS"))
                        return False
            elif self.messaging_type == "SqsConnection":
                self.messaging_constructor_params = (
                    self.get_env_var('AWS_ACCESS_KEY_ID'),
                    self.get_env_var('AWS_ACCESS_KEY_SECRET') or self.get_env_var(
                        'AWS_SECRET_ACCESS_KEY'),
                    self.get_env_var('AWS_REGION'),
                    self.get_env_var('CONSUME_CONFIG_FILE_PATH')
                )
            else:
                logger.error("Invalid MESSAGING_TYPE %s", self.messaging_type)
                return False

        self.service_constructor_params = ()
        return True
