# Use the base image as a parent image
FROM rococo_service_processor:latest
# Set the working directory to /app

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /src/service_processor /app/src/service_processors/
COPY pyproject.toml /app


# Run service.py when the container launches
CMD ["poetry", "run", "python", "src/process.py"]