# Use an official Python runtime as the parent image
FROM python:3.10.4

RUN apt update && \
    apt install -y gcc build-essential libc-dev make git libffi-dev libssl-dev \
    python3-dev libxml2-dev libxslt-dev libjpeg-dev zlib1g libfreetype-dev \
    liblcms2-dev libopenjp2-7-dev libtiff-dev tk-dev tcl-dev wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/*

# Expose port 5060
EXPOSE 5060

# Sets the working directory in the container
WORKDIR /app

# Install Python dependencies
COPY ./src/poetry.lock /app
COPY ./src/pyproject.toml /app

ENV PIP_ROOT_USER_ACTION=ignore

RUN python -m pip install --upgrade pip && \
    python -m pip install --upgrade setuptools && \
    python -m pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# Add directories to the container
COPY ./src /app/src

ENV PYTHONPATH=$PYTHONPATH:/app:/app/src

# Make entrypoint.sh executable
RUN chmod +x /app/src/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/src/entrypoint.sh"]
