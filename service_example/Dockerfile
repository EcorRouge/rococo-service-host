# Use the base image as a parent image
FROM rococo_service_processor
# Set the working directory to /app

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /service_example/__init__.py /app/src/services/__init__.py
COPY /service_example/processor.py /app/src/services/processor.py
COPY /service_example/pyproject.toml /app/src/services/pyproject.toml

# Run service.py when the container launches
CMD ["poetry", "run", "python", "src/process.py"]