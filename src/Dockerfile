# Use an official Python runtime as a parent image
FROM python:3.10.4

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.10 -

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies using Poetry
RUN poetry install

# Run service.py when the container launches
CMD ["poetry", "run", "python", "process.py"]
