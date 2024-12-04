# The image containing build tools & instructions required to produce the runtime docker image
FROM python:3.10-slim-bullseye as builder

# pin build tools and base image version - for reproducible builds
# do not upgrade build image - reproducible builds + lax security requirements

RUN pip install poetry==1.8.3

# POETRY_VIRTUALENVS_CREATE=1 - for now, to support the current situation where
# the Python version in the .toml does not necessarily match the Python version
# the runtime docker image is based on
ENV EXECUTION_TYPE=MESSAGING \
    MESSAGING_TYPE=RabbitMqConnection \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PROCESSOR_MODULE=services.processor \
    PROCESSOR_TYPE=LoggingServiceProcessor \
    PYTHONPATH=/app

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

COPY pyproject.toml /app/src/info/

RUN poetry lock --no-update && poetry install

COPY ./src ./src
COPY ./tests ./tests

CMD ["poetry", "run", "python", "src/process.py"]
