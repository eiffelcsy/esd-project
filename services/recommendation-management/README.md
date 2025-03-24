# Recommendation Management Service

This microservice is responsible for generating travel recommendations using the OpenAI API based on trip dates and destination. It consumes messages from a RabbitMQ queue, processes them, and sends back the recommendations.

## Features

- Consumes trip data messages from RabbitMQ
- Generates travel recommendations using OpenAI's GPT-3.5
- Stores only trip_id and recommendations in PostgreSQL database for persistence
- Provides REST API endpoints for recommendation management
- Publishes recommendation results back to RabbitMQ

## Requirements

- Python 3.9+
- Flask
- PostgreSQL
- RabbitMQ
- OpenAI API key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recommendation_db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Service Configuration
PORT=5002
```

## Installation

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Set up the environment variables as described above
4. Run the service with `python app.py`

## API Endpoints

### Health Check
```
GET /health
```

### Create Recommendation
```
POST /api/recommendations
```
Request body:
```json
{
  "trip_id": "12345",
  "destination": "Paris",
  "start_date": "2023-09-15",
  "end_date": "2023-09-20"
}
```

### Get Recommendation by Trip ID
```
GET /api/recommendations/{trip_id}
```

### Get All Recommendations
```
GET /api/recommendations
```

## Message Format

### Incoming Message
```json
{
  "trip_id": "12345",
  "destination": "Paris",
  "start_date": "2023-09-15",
  "end_date": "2023-09-20"
}
```

### Outgoing Message
```json
{
  "trip_id": "12345",
  "destination": "Paris",
  "start_date": "2023-09-15",
  "end_date": "2023-09-20",
  "recommendations": {
    "attractions": [...],
    "restaurants": [...],
    "activities": [...],
    "events": [...],
    "tips": [...]
  },
  "timestamp": "2023-08-01T12:00:00Z"
}
```

### Database Schema

```
Recommendation
-------------
id: Integer (Primary Key)
trip_id: String (Unique)
recommendations: JSON
created_at: DateTime
updated_at: DateTime
```
