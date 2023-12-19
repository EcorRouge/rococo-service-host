FROM python:3.10

WORKDIR /app

RUN set -x \
   && apt update

# Install cron
RUN set -x \
   && apt install -y cron

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

RUN poetry --version

COPY pyproject.toml poetry.lock* ./

COPY pyproject.toml /app/src/info/

RUN poetry install

COPY ./src ./src
COPY ./tests ./tests

ENV PYTHONPATH /app

ENV MESSAGING_TYPE=RabbitMqConnection
ENV PROCESSOR_TYPE=LoggingServiceProcessor
ENV PROCESSOR_MODULE=services.processor

CMD ["poetry", "run", "python", "src/process.py"]
