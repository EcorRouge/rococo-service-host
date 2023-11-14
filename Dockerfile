FROM python:3.10

WORKDIR /app

RUN python -m pip install --upgrade pip

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

RUN poetry --version

COPY pyproject.toml poetry.lock* ./

RUN poetry install

COPY . .

ENV PYTHONPATH /app

CMD ["poetry", "run", "python", "src/process.py"]
