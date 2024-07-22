# rococo-service-host
A Docker-based host for services that process messages from a queue

## Project structure
rococo_svchost       - runnable service host  
rococo_service_base  - base docker image for the processor services  
service_example      - example of a service runnable via service host  
cron_service_example - example of a service performing work at given intervals  
cron_run_at_example  - example of a service performing work at the certain time  

## Improvements in v 1.0.0 compared to 0.y.y, and the migration plan
- service host version changed to 1.0.0 according to SemVer, the breaking changes and the migration plan are outlined in the BREAKING.md  
- proper dependency resolution between service and service host  
- it is now easily possible to run a service locally  
- the same mechanism is used for both local run and Docker run (`poetry run svchost`)  
- infer service package and processor module from the poetry output and module metadata (PROCESSOR_MODULE / PROCESSOR_TYPE became a fallback)
- the new base Dockerfile for services and its build arguments (e.g. `SVC_ROOT_DIR`) removes the need for the Dockerfile in the most of services - the new `rococo-service-base-onbuild` image can be used directly in the docker compose file. The required environment variables can be specified in the .env files or directly in the docker compose configuration.  
- adds an easy way to use local poetry packages during the development (in the docker container too)

## Environment setup

## How to run a service

### to run locally via terminal
1. cd to the choosen example directory (e.g. rococo-service-host/service_example)  
2. copy `.env.example` to `.env`, `.env.secrets.example` to `.env.secrets`.  
3. run `poetry install` to install the dependencies  
4. run `export $(cat .env | xargs) && export $(cat .env.secrets | xargs)` to export the environment variables into the shell  
5. run `poetry run svchost` in the shell to launch the service  
  
You might see warnings related to the environment variables that have to be configured.  
The following lines indicate that the basic configuration is correct:  
```
[INFO] service_processor_factory:33 - processor_module: service_example.processor
[INFO] service_processor_factory:39 - processor_type: ChildLoggingServiceProcessor
```
Note that the specific processor_module and processor_type will vary depending on the example.  
It is possible to run one service locally, along with the rest of the system being run in the Docker services. This requires proper networking configuration.  

### to run locally via PyCharm
1. cd to the choosen example directory (e.g. rococo-service-host/service_example)  
2. copy `.env.example` to `.env`, `.env.secrets.example` to `.env.secrets`.  
3. run `poetry install` to create virtual environment and install the dependencies.  
4. in PyCharm, create new Run configuration (Python/Poetry)  
   - select virtual environment from step 2
   - select module in the script / module dropdown
   - rococo_svchost.process as a module
   - set the example directory as a working directory
   - configure environment variables (consider using the [EnvFile](https://plugins.jetbrains.com/plugin/7861-envfile) PyCharm plugin)
5. run the configuration via PyCharm

### to debug service running in the Docker container
this should be possible with the [Remote debugging with the Python remote debug server configuration﻿](https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html?_gl=1*1q85n8a*_ga*MTI2MDI0NzgyMy4xNzE1OTM2ODA4*_ga_9J976DJZ68*MTcyMTY0MDgwMS4yMC4wLjE3MjE2NDA4MDEuMC4wLjA.#remote-debug-config). Not tested yet.

### using local package dependencies in the docker image

The use of the `rococo-service-base-onbuild` base image enables an easy way to plug in the local package dependencies.  

For example, to use a local `rococo` package during the `service_example` docker image build:
1. Create `dev_packages` directory in the `service_example` directory.  
2. Place the required `rococo.tar.gz` (or `.whl`) into the `dev_packages` directory
3. Build the image with the `ENVIRONMENT` build argument set to either `local` or `development`  
```bash
docker build . -t service-example  --build-arg ENVIRONMENT=development
```
4. Observe the build log to see the modified .toml file and the information about the replaced packages.  

## Building and publishing

Publishing of the `rococo-service-base-onbuild` docker image, as well as publishing of the `rococo-svchost` PyPi package, is yet to be automated (currently done manually).  

### rococo-service-base-onbuild image
**building:**
```bash
docker ./rococo_service_base -t ecorrouge/rococo-service-base-onbuild:1.0.0 -t ecorrouge/rococo-service-base-onbuild:latest
```
the use of multiple tags is preferrable - it gives the flexibility to always use the latest image via `FROM rococo-service-base-onbuild` or similar docker compose configuration, or pin the service to the specific version.  

**publishing:**
```bash
docker login  # <- perform login
docker push ecorrouge/rococo-service-base-onbuild --all-tags
docker logout
```

### rococo-svchost PyPi package
**building:**
1. cd to the `rococo_svchost` directory  
2. run `poetry build`  

**publishing:**
This step is to be automated, similar to the rococo package publishing.  
As of now, to build and publish manually:

1. set PyPi API token in poetry by running `poetry config pypi-token.pypi your-api-token`
2. cd to the `rococo_svchost` directory
3. run `poetry publish --build`, or
```bash
poetry build
poetry publish
```

## Creating a child image - custom processors

Use the example in the "cron_service_example" folder. What you need to do is:
- create a `processor.py` file with the Class for the processor, the class has to have `process` method.
- create the `__init__.py` file importing the processor file
- have a `pyproject.toml` for it, make sure that the project structure is such that it can be build via `poetry install` / `poetry build` 


If your service requires queue message processing, use "service_example" folder as an example.

- derive processor class from the `Rococo.messaging.BaseServiceProcessor`.  
- create the env var `< processor_class_name >_QUEUE_NAME` = `< your_rabbit_mq_queue_name >`  
- `QUEUE_NAME_PREFIX` value is optional but the var needs to be provided  
- the queue name that is formed is `queue_name_prefix+processor_class_name+_QUEUE_NAME`  


## Development

These are instructions for building the dev environment of the service host.

### RabitMQ image

```bash
docker network create rabbitmq-network
docker run -d --net=rabbitmq-network --name some-rabbit -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=rabbituser -e RABBITMQ_DEFAULT_PASS=rabbituserpass rabbitmq:3-management
```

to run a service docker image with the above rabbitmq attached:
```bash
docker build . -t service-example  --build-arg ENVIRONMENT=development
docker run --net=rabbitmq-network --env-file ./.env --env-file ./.env.secrets --name service-example service-example
```


## Cron processor

If you are making a processor based on cron execution, these are the only env vars needed:

- EXECUTION_TYPE=CRON
- CRON_TIME_AMOUNT=time_in_int_or_float    (example : CRON_TIME_AMOUNT=30 or CRON_TIME_AMOUNT=0.5 )
- CRON_TIME_UNIT=time_in_units    (one of [SECONDS,MINUTES,HOURS,DAYS,WEEKS] , example = CRON_TIME_UNIT=SECONDS)

An example setup of a cron processor image is at "/cron_service_example"

Naturally, you wont need a RabbitMQ server nor listener for a cron processor, so the processor doesn't need a class that extends BaseServiceProcessor from rococo messaging.