# Use the base image as a parent image
FROM rococo-service-host

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./__init__.py /app/src/services/__init__.py
COPY ./processor.py /app/src/services/processor.py
COPY ./pyproject.toml /app/pyproject.toml

# Install dependencies using Poetry
RUN poetry install

ENV PROCESSOR_MODULE=services.processor
ENV PROCESSOR_TYPE=LoggingServiceProcessor
ENV EXECUTION_TYPE=CRON
ENV CRON_TIME_AMOUNT=30
ENV CRON_TIME_UNIT=SECONDS

# Run service.py when the container launches
CMD ["poetry", "run", "python", "src/process.py"]