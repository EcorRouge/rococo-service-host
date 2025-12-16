ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}

WORKDIR /app

RUN set -x \
   && apt update

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

RUN poetry --version

COPY pyproject.toml poetry.lock* ./

COPY pyproject.toml /app/src/info/

RUN poetry lock && poetry install --no-root

COPY ./src ./src
COPY ./tests ./tests

ENV PYTHONPATH=/app

ENV MESSAGING_TYPE=RabbitMqConnection
ENV PROCESSOR_TYPE=LoggingServiceProcessor
ENV PROCESSOR_MODULE=services.processor
ENV EXECUTION_TYPE=MESSAGING

CMD ["poetry", "run", "python", "src/process.py"]
