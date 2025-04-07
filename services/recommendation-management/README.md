# Recommendation Management Service

This service is responsible for generating AI-powered travel recommendations for trips. It listens for requests via RabbitMQ, processes them using the OpenAI API, and publishes the results back to RabbitMQ.

## Architecture

The Recommendation Management Service operates as a pure message processor with the following flow:

1. Listens for messages on the `recommendation_requests` RabbitMQ queue
2. Processes requests by calling the OpenAI API to generate recommendations
3. Publishes results to the `recommendation_responses` queue
4. The trip-management service consumes these responses and stores the recommendations

## Key Components

- **Message Broker**: Handles RabbitMQ connectivity and message processing
- **OpenAI Service**: Interfaces with the OpenAI API to generate recommendations
- **In-Memory Cache**: Prevents duplicate processing of requests

## Environment Variables

Configure the service using these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `RABBITMQ_HOST`: RabbitMQ host (default: "rabbitmq")
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USER`: RabbitMQ username (default: "guest")
- `RABBITMQ_PASS`: RabbitMQ password (default: "guest")

## Development Setup

1. Clone the repository
2. Create a `.env` file with your environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run the service: `python app.py`

## Docker Deployment

```bash
docker build -t recommendation-management .
docker run -d --name recommendation-management recommendation-management
```

## Testing

The `tests` directory contains several scripts for testing:

- `tests/test_send.py`: Test sending recommendation requests to RabbitMQ
- `tests/test_receive.py`: Test receiving recommendation responses from RabbitMQ

To run the tests, you need RabbitMQ running. Then execute:

```bash
python tests/test_send.py
python tests/test_receive.py
```
