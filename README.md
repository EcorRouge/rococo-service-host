# rococo-service-host
A Docker-based host for services that process messages from a queue


## Processing
The docker image's main process is `process.py` which handles all message processing.

## Setup docker-compose variables
Within docker-compose.yml you need to set up the variables for each service that's going to be used. 
Change these:

- RABBITMQ_HOST=your_rabbitmq_host
- RABBITMQ_QUEUE=your_queue_name

- AWS_ACCESS_KEY=your_aws_access_key
- AWS_SECRET_KEY=your_aws_secret_key
- AWS_REGION=your_aws_region
- SQS_QUEUE_URL=your_sqs_queue_url



## build and run docker image
RABBITMQ_HOST (optional, defaults to False = RabbitMQ Service not executing)
if RABBITMQ_HOST is not provided, the env vars below are not required:
RABBITMQ_PORT
RABBITMQ_QUEUE
RABBITMQ_USERNAME
RABBITMQ_PASSWORD
RABBITMQ_VIRTUAL_HOST (optional, defaults to '')
RABBITMQ_NUM_THREADS (optional, defaults to 1)

`docker run --name=rococo-service-processor -e RABBITMQ_HOST=your_rabbit_host -e ....rest_of_env_vars`

