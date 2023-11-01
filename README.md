# rococo-service-host
A Docker-based host for services that process messages from a queue


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
How to run both services:
`docker-compose up -d --build`
How to run RabbitMQ
`docker-compose up -d rabbitmq-service --build`
How to run Amazon SQS
`docker-compose up -d sqs-service --build`
