ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}

WORKDIR /app

# Install Poetry and verify installation
RUN set -x \
   && apt-get update \
   && apt-get install -y --no-install-recommends curl ca-certificates \
   && rm -rf /var/lib/apt/lists/* \
   && curl -sSL --proto '=https' --tlsv1.2 https://install.python-poetry.org | POETRY_HOME=/opt/poetry python \
   && cd /usr/local/bin \
   && ln -s /opt/poetry/bin/poetry \
   && poetry config virtualenvs.create false \
   && poetry --version

COPY pyproject.toml ./
COPY poetry.lock ./

COPY pyproject.toml /app/src/info/

RUN poetry lock && poetry install --no-root

COPY ./src ./src
COPY ./tests ./tests

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PYTHONPATH=/app

ENV MESSAGING_TYPE=RabbitMqConnection
ENV PROCESSOR_TYPE=LoggingServiceProcessor
ENV PROCESSOR_MODULE=services.processor
ENV EXECUTION_TYPE=MESSAGING

CMD ["poetry", "run", "python", "src/process.py"]
