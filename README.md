# rococo-service-host

A Docker-based host for services that process messages from a queue


## Processing

The docker image's main process is `process.py` which handles all message processing.


## set up the env file

See .env.example and make an .env file inside src folder


## build and run docker image

```bash
cd src
docker build -t rococo-service-processor .
docker run --env-file ./.env --name rococo-service-processor rococo-service-processor
```
## Linting

```bash
poetry run pylint src
```

## Tests (deprecated - tests are not copied to the docker image - WIP)

using terminal inside the docker image:

```bash
poetry run pytest -vv
```

=========================================================== test session starts ===========================================================
platform linux -- Python 3.10.4, pytest-7.4.3, pluggy-1.3.0 -- /root/.cache/pypoetry/virtualenvs/src-9TtSrW0h-py3.10/bin/python
cachedir: .pytest_cache
rootdir: /app
plugins: anyio-4.0.0
collected 1 item                                                                                                                          

tests/test_message.py::test_rabbitmq_send_message PASSED                                                                            [100%]

============================================================ 1 passed in 0.03s ============================================================
