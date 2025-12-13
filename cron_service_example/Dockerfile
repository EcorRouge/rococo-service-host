# Use the base image as a parent image
ARG BASE_IMAGE_VERSION=0.1.21
FROM rococo-service-host:${BASE_IMAGE_VERSION}

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./__init__.py /app/src/services/__init__.py
COPY ./processor.py /app/src/services/processor.py
COPY ./pyproject.toml /app/pyproject.toml

# Install dependencies using Poetry and ensure proper ownership for the non-root user
RUN poetry install \
    && chown -R appuser:appuser /app

# Switch to non-root user (inherited from base image)
USER appuser

ENV PROCESSOR_MODULE=services.processor
ENV PROCESSOR_TYPE=LoggingServiceProcessor
ENV EXECUTION_TYPE=CRON
ENV CRON_TIME_AMOUNT=30
ENV CRON_TIME_UNIT=SECONDS
ENV CRON_RUN_AT=
# Run service.py when the container launches
CMD ["poetry", "run", "python", "src/process.py"]