# Use the base image as a parent image
FROM rococo-service-host

# Copy the current directory contents into the container at /app
COPY ./__init__.py /app/src/services/__init__.py
COPY ./processor.py /app/src/services/processor.py
COPY ./pyproject.toml /app/pyproject.toml

# Install dependencies using Poetry
RUN poetry lock --no-update && poetry install

ENV MESSAGING_TYPE=RabbitMqConnection \
    PROCESSOR_TYPE=ChildLoggingServiceProcessor \
    PROCESSOR_MODULE=services.processor
