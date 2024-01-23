"""
Host Config class
"""
import logging
from rococo.config import BaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO)


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
                self.get_env_var("MESSAGING_TYPE") not in ["RabbitMqConnection"]):
            logging.error("Invalid value for MESSAGING_TYPE env var %s",
                        self.get_env_var("MESSAGING_TYPE"))
            return False
        if (self.get_env_var("EXECUTION_TYPE") not in ["CRON"]) and (
            self.get_env_var("PROCESSOR_TYPE") is None):
            logging.error("Invalid value for PROCESSOR_TYPE env var %s",
                        self.get_env_var("PROCESSOR_TYPE"))
            return False
        if self.get_env_var("PROCESSOR_MODULE") is None:
            logging.error("Invalid value for PROCESSOR_MODULE env var %s",
                        self.get_env_var("PROCESSOR_MODULE"))
            return False
        if self.get_env_var("EXECUTION_TYPE") == "CRON":
            if self.get_env_var("CRON_TIME_AMOUNT") is None:
                logging.error("Invalid value for CRON_TIME_AMOUNT env var %s",
                        self.get_env_var("CRON_TIME_AMOUNT"))
                return False
            try:
                float(self.get_env_var("CRON_TIME_AMOUNT"))
            except Exception as e: # pylint: disable=W0718
                logging.error("Exception %s. Invalid value for CRON_TIME_AMOUNT env var %s",
                              e,
                              self.get_env_var("CRON_TIME_AMOUNT"))
                return False
            valid_cron_units = ['seconds','minutes','hours','days','weeks']
            if self.get_env_var("CRON_TIME_UNIT").lower() not in valid_cron_units:
                logging.error("Invalid value for CRON_TIME_UNIT env var %s. Expected one of %s",
                        self.get_env_var("CRON_TIME_UNIT").lower(),
                        valid_cron_units)
                return False

        
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
                    self.get_env_var('RABBITMQ_VIRTUAL_HOST'))
                if self.get_env_var("RABBITMQ_NUM_THREADS"):
                    try:
                        self.num_threads = int(self.get_env_var("RABBITMQ_NUM_THREADS"))
                    except TypeError:
                        logging.error("Invalid value for RABBITMQ_NUM_THREADS %s . Expected int",
                                    self.get_env_var("RABBITMQ_NUM_THREADS"))
                        return False
            else:
                logging.error("Invalid MESSAGING_TYPE %s", self.messaging_type)
                return False
            
        self.service_constructor_params = ()
        return True
