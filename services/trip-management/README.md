# Trip Management Service

This service is responsible for managing trips in the travel planning application. It acts as a composite service that coordinates between various other microservices to handle trip creation, itinerary management, and travel recommendations.

## Features

- Create and manage trips
- Coordinate with itinerary service for trip planning
- Integrate with recommendation service for travel suggestions
- Handle both HTTP and AMQP communication

## Architecture

The service follows a microservices architecture and communicates with other services via:
- HTTP REST APIs for synchronous communication
- RabbitMQ for asynchronous message-based communication

## Prerequisites

- Python 3.8+
- PostgreSQL
- RabbitMQ

## Environment Variables

Create a `.env` file with the following variables:

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/trip_db
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
PORT=5001
```

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Service

1. Start the service:
   ```bash
   python app.py
   ```

2. The service will be available at `http://localhost:5001`

## API Endpoints

### HTTP Endpoints

- `GET /health` - Health check endpoint
- `POST /trips` - Create a new trip
- `GET /trips/<trip_id>` - Get trip details
- `GET /users/<user_id>/trips` - Get all trips for a user
- `PUT /trips/<trip_id>/itinerary` - Update trip itinerary

### Message Queue Topics

- Consumes from: `trip_queue` - For trip creation requests
- Publishes to: `recommendation_queue` - For recommendation requests

## Testing

Run the tests using:
```bash
python -m unittest discover tests
```

## Docker

Build the container:
```bash
docker build -t trip-management .
```

Run the container:
```bash
docker run -p 5001:5001 --env-file .env trip-management
```
