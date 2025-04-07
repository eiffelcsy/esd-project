# Recommendation Management Service

The Recommendation Management Service provides AI-powered travel recommendations for trips. It uses OpenAI's API to generate personalized suggestions for destinations, activities, and more.

## Endpoints

### Health Check

```
GET /health
```

Returns health status of the service, including database and message queue connectivity.

**Response:**
```json
{
  "status": "healthy",
  "service": "recommendation-management",
  "database_status": "connected",
  "recommendation_count": 15,
  "cached_trip_ids": 3
}
```

### Root Endpoint

```
GET /
```

Service information endpoint.

**Response:**
```json
{
  "message": "Recommendation Management Service API. Use /health for health check."
}
```

### Create Recommendation

```
POST /api/recommendations
```

Creates a new recommendation for a trip.

**Request:**
```json
{
  "trip_id": 123,
  "destination": "Paris",
  "start_date": "2023-11-05T00:00:00",
  "end_date": "2023-11-12T00:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "trip_id": "123",
  "recommendations": {
    "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
    "restaurants": ["Le Jules Verne", "L'Ambroisie", "Le Cinq"],
    "activities": ["Seine River Cruise", "Wine Tasting", "Walking Tour of Montmartre"],
    "day_trips": ["Versailles Palace", "Giverny", "Loire Valley"]
  },
  "created_at": "2023-10-25T14:30:45"
}
```

### Get Recommendation by Trip ID

```
GET /api/recommendations/{trip_id}
```

Retrieves recommendations for a specific trip.

**Response:**
```json
{
  "id": 1,
  "trip_id": "123",
  "recommendations": {
    "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
    "restaurants": ["Le Jules Verne", "L'Ambroisie", "Le Cinq"],
    "activities": ["Seine River Cruise", "Wine Tasting", "Walking Tour of Montmartre"],
    "day_trips": ["Versailles Palace", "Giverny", "Loire Valley"]
  },
  "created_at": "2023-10-25T14:30:45"
}
```

### Get All Recommendations

```
GET /api/recommendations
```

Retrieves all recommendations stored in the service.

**Response:**
```json
[
  {
    "id": 1,
    "trip_id": "123",
    "recommendations": {
      "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
      "restaurants": ["Le Jules Verne", "L'Ambroisie", "Le Cinq"],
      "activities": ["Seine River Cruise", "Wine Tasting", "Walking Tour of Montmartre"],
      "day_trips": ["Versailles Palace", "Giverny", "Loire Valley"]
    },
    "created_at": "2023-10-25T14:30:45"
  },
  {
    "id": 2,
    "trip_id": "124",
    "recommendations": {
      "attractions": ["Colosseum", "Vatican Museums", "Trevi Fountain"],
      "restaurants": ["La Pergola", "Il Pagliaccio", "Roscioli"],
      "activities": ["Food Tour", "Vespa Ride", "Gladiator School"],
      "day_trips": ["Pompeii", "Tivoli", "Tuscany"]
    },
    "created_at": "2023-10-26T10:15:30"
  }
]
```

### Test OpenAI Integration

```
GET /api/test/openai?destination={destination}
```

Tests the OpenAI API integration with an optional destination parameter.

**Response:**
```json
{
  "status": "success",
  "message": "OpenAI integration test successful",
  "sample_data": {
    "attractions": ["Example Attraction 1", "Example Attraction 2"],
    "restaurants": ["Example Restaurant 1", "Example Restaurant 2"],
    "activities": ["Example Activity 1", "Example Activity 2"],
    "day_trips": ["Example Day Trip 1", "Example Day Trip 2"]
  }
}
```

### Test RabbitMQ Connectivity

```
GET /api/test/rabbitmq
```

Tests RabbitMQ connection and queue declarations.

**Response:**
```json
{
  "status": "success",
  "message": "Successfully connected to RabbitMQ",
  "queues_declared": ["recommendation_requests", "recommendation_responses"]
}
```

## Message Queue Integration

The service uses RabbitMQ for asynchronous communication with other services:

- **Listens on:** `recommendation_requests` queue
- **Publishes to:** `recommendation_responses` queue

Recommendation requests can be sent via the REST API or through the message queue.

## Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@recommendation-db:5432/recommendation_db`)
- `OPENAI_API_KEY`: Your OpenAI API key
- `RABBITMQ_HOST`: RabbitMQ server address (default: `rabbitmq`)
- `RABBITMQ_PORT`: RabbitMQ server port (default: `5672`)
- `RABBITMQ_USER`: RabbitMQ username (default: `guest`)
- `RABBITMQ_PASS`: RabbitMQ password (default: `guest`)

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5002
```
