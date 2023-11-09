# Use the base image as a parent image
FROM ecorrouge/rococo-service-host:latest
# Set the working directory to /app

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /src/service_processors /app/src/service_processors/


# Run service.py when the container launches
CMD ["poetry", "run", "python", "src/process.py"]