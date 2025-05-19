+# rococo-service-host
A Docker-based host for services that process messages from a queue

## Processing
The docker image's main process is `process.py` which handles all message processing.

## set up the env file

- Copy `.env.example` to `.env` at project root
- Copy `.env.secrets.example` to `.env.secrets` at project root

## Building and publishing

When you merge code to main branch, the image will be built and published automatically to the dockerhub repository.


## Creating a child image - custom processors

Use the example in "service_example" folder. What you need to do is:
- create a `processor.py` file with the Class for the processor
- create the `__init__.py` file importing it
- have a `pyproject.toml` for it
- copy all 3 files into `/app/src/services/` in the target image
- have an env var in your Dockerfile with `PROCESSOR_TYPE` that specifies the Class, and `PROCESSOR_MODULE` which specifies the module to import, which is usually `services.processor`  if you named your file `processor.py`
- after you named your processor class, you must create the env var `< processor_class_name >_QUEUE_NAME` = `< your_rabbit_mq_queue_name >`
- `QUEUE_NAME_PREFIX` value is optional but the var needs to be provided
- The queue name that is formed is `queue_name_prefix+processor_class_name+_QUEUE_NAME`

In this case you can test the service_example child image

From project root do:

```bash
cd service_example
docker network create rabbitmq-network
docker run -d --net=rabbitmq-network --name some-rabbit -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
docker build -t custom-service-processor .
docker run --net=rabbitmq-network --env-file ./.env --env-file ./.env.secrets --name custom-service-processor custom-service-processor
```

Tests for child
```bash
docker exec -it custom-service-processor poetry run pytest -vv
```


For a child of a cron processor:

```bash
cd cron_service_example
docker build -t cron-service-processor .
docker run --env-file ./.env --name cron-service-processor cron-service-processor
```

No tests are setup for cron processor thus far.


## Development

These are instructions for building the dev environment of the service host.

### RabitMQ image

```bash
docker network create rabbitmq-network
docker run -d --net=rabbitmq-network --name some-rabbit -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
```


### Service host image

```bash
docker network create rabbitmq-network
docker build -t rococo-service-host .
docker run --net=rabbitmq-network --env-file ./.env --env-file ./.env.secrets --name rococo-service-host rococo-service-host
```

### Test

```bash
docker exec -it rococo-service-host poetry run pytest -vv
```

## Cron processor

If you are making a processor based on cron execution, these are the only env vars needed at Dockerfile level

- PROCESSOR_MODULE=your.processor.module
- EXECUTION_TYPE=CRON
- CRON_EXPRESSIONS=one or more cron expressions. (example : CRON_EXPRESSIONS="* * * * *") If provided, the rest of the CRON_\* env vars are ignored.
- CRON_TIME_AMOUNT=time_in_int_or_float    (example : CRON_TIME_AMOUNT=30 or CRON_TIME_AMOUNT=0.5 )
- CRON_TIME_UNIT=time_in_units    (one of [SECONDS,MINUTES,HOURS,DAYS,WEEKS] , example = CRON_TIME_UNIT=SECONDS)

An example setup of a cron processor image is at "/cron_service_example"

Naturally, you wont need a RabbitMQ server nor listener for a cron processor, so the processor doesn't need a class that extends BaseServiceProcessor from rococo messaging.