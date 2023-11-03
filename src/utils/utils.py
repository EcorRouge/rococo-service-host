import os
import re
import logging
import traceback

logging.basicConfig(level=logging.INFO)

def read_project_version(project_dir):
    # Read pyproject.toml and extract the version using regular expression
    toml_path = os.path.join(project_dir, 'pyproject.toml')
    try:
        with open(toml_path, 'r') as file:
            pyproject_content = file.read()
            version_match = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', pyproject_content)
            if version_match:
                version = version_match.group(1)
                logging.info(f'Project Version: {version}')
            else:
                logging.warning('Version not found in pyproject.toml.')
    except FileNotFoundError:
        logging.error('pyproject.toml not found.')

