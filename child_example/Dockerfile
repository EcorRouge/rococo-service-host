# Use the base image as a parent image
FROM rococo_service_processor
# Set the working directory to /app

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /services/ /app/src/services/

# Run service.py when the container launches
CMD ["poetry", "run", "python", "src/process.py"]