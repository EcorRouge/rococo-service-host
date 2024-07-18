# rococo-service-base-onbuild
# This is a base image for the Rococo services
FROM python:3.10-slim-bullseye

# pin build tools and base image version - for reproducible builds
# do not upgrade build image - reproducible builds + lax security requirements

RUN pip install poetry==1.8.3 tomlkit==0.12

# POETRY_VIRTUALENVS_CREATE=1 - for now, to support the current situation where
# the Python version in the .toml does not necessarily match the Python version
# the runtime docker image is based on
ENV EXECUTION_TYPE=MESSAGING \
    MESSAGING_TYPE=RabbitMqConnection \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY ./use_local_deps_in_toml.py ./
ONBUILD ARG  SVC_ROOT_DIR="./"
ONBUILD COPY ${SVC_ROOT_DIR} ./

ONBUILD ARG ENVIRONMENT=production
ONBUILD RUN \
    export ENVIRONMENT=${ENVIRONMENT} && \
    python use_local_deps_in_toml.py ./pyproject.toml && \
    \
    echo "\n============ pyproject.toml (${ENVIRONMENT}) ============" && \
    cat -n ./pyproject.toml && \
    echo "\n============ pyproject.toml END =========================\n" && \
    \
    touch README.md && \
    poetry install && \
    rm -rf $POETRY_CACHE_DIR

CMD ["poetry", "run", "svchost"]