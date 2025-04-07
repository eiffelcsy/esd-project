# Itinerary Service

The Itinerary Service manages detailed travel itineraries, including daily activities, recommendations, and scheduling. It integrates with the Recommendation Service to provide AI-powered suggestions for trip activities.

## Endpoints

### Health Check

```
GET /health
```

Returns the service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "itinerary",
  "rabbitmq_status": "connected"
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
  "message": "Itinerary Service API. Use /health for health check."
}
```

### Get Itinerary

```
GET /api/itinerary/{trip_id}
```

Retrieves an itinerary for a specific trip. Creates a new itinerary if one doesn't exist.

**Response:**
```json
{
  "trip_id": "123",
  "destination": "Paris",
  "start_date": "2023-07-01",
  "end_date": "2023-07-08",
  "daily_activities": {
    "2023-07-01": [
      {
        "name": "Eiffel Tower Visit",
        "date": "2023-07-01",
        "time": "10:00",
        "end_time": "12:00",
        "location": "Eiffel Tower, Paris",
        "notes": "Bring camera"
      }
    ],
    "2023-07-02": [
      {
        "name": "Louvre Museum",
        "date": "2023-07-02",
        "time": "09:00",
        "end_time": "13:00",
        "location": "Louvre Museum, Paris",
        "notes": "Audio guide recommended"
      }
    ]
  },
  "created_at": "2023-06-15T12:30:45"
}
```

### Create Itinerary

```
POST /api/itinerary
```

Creates a new itinerary for a trip and requests recommendations.

**Request:**
```json
{
  "trip_id": "123",
  "destination": "Paris",
  "start_date": "2023-07-01T00:00:00",
  "end_date": "2023-07-08T00:00:00"
}
```

**Response:**
```json
{
  "trip_id": "123",
  "destination": "Paris",
  "start_date": "2023-07-01",
  "end_date": "2023-07-08",
  "daily_activities": {},
  "created_at": "2023-06-15T14:25:10"
}
```

### Add Activity

```
PUT /api/itinerary/{trip_id}/activities
```

Adds an activity to an itinerary.

**Request:**
```json
{
  "name": "Notre Dame Cathedral",
  "date": "2023-07-03",
  "time": "11:00",
  "end_time": "13:00",
  "location": "Notre Dame Cathedral, Paris",
  "notes": "Check for opening hours"
}
```

**Response:**
```json
{
  "message": "Activity added successfully"
}
```

### Delete Activity

```
DELETE /api/itinerary/{trip_id}/activities
```

Deletes an activity from an itinerary.

**Request:**
```json
{
  "date": "2023-07-03",
  "index": 0
}
```

**Response:**
```json
{
  "message": "Activity deleted successfully"
}
```

### Delete Itinerary

```
DELETE /api/itinerary/{trip_id}
```

Deletes an entire itinerary.

**Response:**
```json
{
  "message": "Itinerary deleted successfully"
}
```

### Request Recommendations

```
POST /api/recommendations
```

Requests AI-powered travel recommendations for a trip.

**Request:**
```json
{
  "trip_id": "123",
  "destination": "Paris",
  "start_date": "2023-07-01T00:00:00",
  "end_date": "2023-07-08T00:00:00"
}
```

**Response:**
```json
{
  "message": "Recommendation request sent. Results will be available asynchronously."
}
```

### Get Recommendations

```
GET /api/recommendations/{trip_id}
```

Retrieves recommendations for a specific trip.

**Response:**
```json
{
  "trip_id": "123",
  "recommendations": {
    "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
    "restaurants": ["Le Jules Verne", "L'Ambroisie", "Le Cinq"],
    "activities": ["Seine River Cruise", "Wine Tasting", "Walking Tour of Montmartre"],
    "day_trips": ["Versailles Palace", "Giverny", "Loire Valley"]
  },
  "created_at": "2023-06-15T15:10:30"
}
```

### Add Recommended Activity

```
POST /api/itinerary/{trip_id}/add_recommended_activity
```

Adds a recommended activity to the itinerary.

**Request:**
```json
{
  "activity_name": "Eiffel Tower",
  "date": "2023-07-04",
  "time": "14:00",
  "end_time": "16:00"
}
```

**Response:**
```json
{
  "message": "Recommended activity added successfully",
  "activity": {
    "name": "Eiffel Tower",
    "date": "2023-07-04",
    "time": "14:00",
    "end_time": "16:00",
    "location": "Eiffel Tower, Paris",
    "notes": "Famous iron tower offering city views"
  }
}
```

### Add Recommendations

```
POST /api/itinerary/{trip_id}/recommendations
```

Adds a set of recommendations to an itinerary.

**Request:**
```json
{
  "recommendations": {
    "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
    "restaurants": ["Le Jules Verne", "L'Ambroisie", "Le Cinq"],
    "activities": ["Seine River Cruise", "Wine Tasting", "Walking Tour of Montmartre"],
    "day_trips": ["Versailles Palace", "Giverny", "Loire Valley"]
  }
}
```

**Response:**
```json
{
  "message": "Recommendations added successfully"
}
```

### Test RabbitMQ Connectivity

```
GET /api/test/rabbitmq
```

Tests RabbitMQ connection and messaging capabilities.

**Response:**
```json
{
  "status": "success",
  "message": "RabbitMQ connection test successful",
  "details": {
    "connected": true,
    "queues_declared": ["recommendation_requests", "recommendation_responses"]
  }
}
```

## RabbitMQ Integration

The Itinerary Service uses RabbitMQ for asynchronous communication with other services:

- **Publishes to:** `recommendation_requests` queue to request travel recommendations
- **Consumes from:** `recommendation_responses` queue to receive recommendation results
- **Consumes from:** `trip_events` queue to receive trip creation notifications

## Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@itinerary-db:5432/itinerary_db`)
- `RABBITMQ_HOST`: RabbitMQ server address (default: `rabbitmq`)
- `RABBITMQ_PORT`: RabbitMQ server port (default: `5672`)
- `RECOMMENDATION_SERVICE_URL`: URL of the Recommendation Service (default: `http://recommendation-management:5002`)

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5006
```
