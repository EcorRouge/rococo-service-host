import os
import re
import logging
import traceback

logging.basicConfig(level=logging.INFO)

def read_project_version(project_dir):
    """
    Reads project version from pyproject.toml

    Args:
        project_dir (str) : src root dir
    """
    # Read pyproject.toml and extract the version using regular expression
    toml_path = os.path.join(project_dir, 'pyproject.toml')
    try:
        with open(toml_path, 'r',encoding='utf-8') as file:
            pyproject_content = file.read()
            version_match = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', pyproject_content)
            if version_match:
                version = version_match.group(1)
                logging.info('Project Version: %s',version)
            else:
                logging.warning('Version not found in pyproject.toml.')
    except FileNotFoundError:
        logging.error('pyproject.toml not found.')


def get_required_env():
    """
    Checks for required env vars from the .env file
    """
    try:
        if not os.environ.get("MESSAGING_TYPE",False):
            raise ValueError("MESSAGING_TYPE is missing.")
        if os.environ.get("MESSAGING_TYPE") not in ["RABBITMQ","SQS"]:
            raise ValueError("Unexpected MESSAGE_TYPE value.")
        if os.environ.get("MESSAGING_TYPE") == "RABBITMQ":
            required_variable_names = ["HOST","QUEUE_NAME","USERNAME","PASSWORD"]
            missing_variables = []
            for variable_name in required_variable_names:
                if os.environ.get(variable_name) is None:
                    missing_variables.append(variable_name)
            if missing_variables:
                raise ValueError(
                    f"Environment variables {', '.join(missing_variables)} are missing.")
            int(os.environ.get("PORT"))
            if os.environ.get("RABBITMQ_NUM_THREADS",False):
                if int(os.environ.get("RABBITMQ_NUM_THREADS"))<=0:
                    raise ValueError("RABBITMQ_NUM_THREADS cant be lower than 1")
    except ValueError as e:
        logging.error(traceback.format_exc())
        logging.error(e)
        return False
    return True
