# rococo-service-host
A Docker-based host for services that process messages from a queue

## Processing
The docker image's main process is `process.py` which handles all message processing.

## set up the env file
Copy `.env.example` to `.env` at project root

## Run & Test with docker compose
```bash
docker compose up -d --build
docker exec -it rococo_service_processor poetry run pytest -vv
```
#### Output
```shell
=========================================================== test session starts ===========================================================
platform linux -- Python 3.10.4, pytest-7.4.3, pluggy-1.3.0 -- /root/.cache/pypoetry/virtualenvs/src-9TtSrW0h-py3.10/bin/python
cachedir: .pytest_cache
rootdir: /app
plugins: anyio-4.0.0
collected 1 item                                                                                                                          

tests/test_message.py::test_rabbitmq_send_message PASSED                                                                            [100%]

============================================================ 1 passed in 0.03s ============================================================
```

## Creating a child image - custom processors

Use the example in "service_example" folder. What you need to do is:
- create a `processor.py` file with the Class for the processor
- create the `__init__.py` file importing it
- have a `pyproject.toml` for it
- copy all 3 files into `/app/src/services/` in the target image
- have an env var with `PROCESSOR_TYPE` that specifies the Class, and PROCESSOR_MODULE which specifies the module to import, which is usually `services.processor`  if you named your file `processor.py`

From project root do:

```bash
docker build -t custom_service_processor -f ./service_example/Dockerfile .
docker run --name custom_service_processor_img --env-file .env.child custom_service_processor
```

Tests for child
```bash
docker exec -it custom_service_processor_img poetry run pytest -vv
```