# Trip Management Service

The Trip Management Service handles the creation and management of trip details. It acts as a central service that coordinates with other services such as Itinerary Service to create comprehensive travel plans.

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
  "service": "trip-management"
}
```

### Create Trip

```
POST /api/trips
```

Creates a new trip and initiates the creation of an associated itinerary.

**Request:**
```json
{
  "user_id": 1,
  "city": "Paris",
  "start_date": "2023-07-01T00:00:00Z",
  "end_date": "2023-07-08T00:00:00Z",
  "group_id": 2
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "city": "Paris",
  "start_date": "2023-07-01T00:00:00Z",
  "end_date": "2023-07-08T00:00:00Z",
  "group_id": 2,
  "itinerary_id": 1,
  "created_at": "2023-06-15T12:30:45",
  "updated_at": "2023-06-15T12:30:45"
}
```

### Get Trip

```
GET /api/trips/{trip_id}
```

Retrieves details for a specific trip.

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "city": "Paris",
  "start_date": "2023-07-01T00:00:00Z",
  "end_date": "2023-07-08T00:00:00Z",
  "group_id": 2,
  "itinerary_id": 1,
  "created_at": "2023-06-15T12:30:45",
  "updated_at": "2023-06-15T12:30:45"
}
```

### Get User Trips

```
GET /api/users/{user_id}/trips
```

Retrieves all trips for a specific user.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "city": "Paris",
    "start_date": "2023-07-01T00:00:00Z",
    "end_date": "2023-07-08T00:00:00Z",
    "group_id": 2,
    "itinerary_id": 1,
    "created_at": "2023-06-15T12:30:45",
    "updated_at": "2023-06-15T12:30:45"
  },
  {
    "id": 2,
    "user_id": 1,
    "city": "Rome",
    "start_date": "2023-08-15T00:00:00Z",
    "end_date": "2023-08-22T00:00:00Z",
    "group_id": null,
    "itinerary_id": 2,
    "created_at": "2023-06-20T09:45:30",
    "updated_at": "2023-06-20T09:45:30"
  }
]
```

### Get Group Trips

```
GET /api/groups/{group_id}/trips
```

Retrieves all trips associated with a specific group.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "city": "Paris",
    "start_date": "2023-07-01T00:00:00Z",
    "end_date": "2023-07-08T00:00:00Z",
    "group_id": 2,
    "itinerary_id": 1,
    "created_at": "2023-06-15T12:30:45",
    "updated_at": "2023-06-15T12:30:45"
  },
  {
    "id": 3,
    "user_id": 2,
    "city": "Barcelona",
    "start_date": "2023-09-10T00:00:00Z",
    "end_date": "2023-09-17T00:00:00Z",
    "group_id": 2,
    "itinerary_id": 3,
    "created_at": "2023-06-25T14:20:15",
    "updated_at": "2023-06-25T14:20:15"
  }
]
```

### Update Trip Itinerary

```
PUT /api/trips/{trip_id}/itinerary
```

Updates the itinerary associated with a trip.

**Request:**
```json
{
  "activities": [
    {
      "name": "Eiffel Tower Visit",
      "date": "2023-07-02",
      "time": "10:00",
      "end_time": "12:00",
      "location": "Eiffel Tower, Paris"
    },
    {
      "name": "Louvre Museum Tour",
      "date": "2023-07-03",
      "time": "14:00",
      "end_time": "17:00",
      "location": "Louvre Museum, Paris"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Itinerary updated successfully"
}
```

### Delete Trip

```
DELETE /api/trips/{trip_id}
```

Deletes a trip and its associated itinerary.

**Response:**
```json
{
  "message": "Trip deleted successfully"
}
```

## RabbitMQ Integration

The Trip Management Service uses RabbitMQ for asynchronous communication with other services:

- **Publishes:** Trip creation events to notify other services
- **Consumes:** Feedback from other services (e.g., itinerary creation confirmation)

## Service Integration

The Trip Management Service integrates with:

- **Itinerary Service**: To create and manage detailed travel itineraries
- **Recommendation Service**: Indirectly, through the Itinerary Service for travel recommendations

## Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@trip-db:5432/trip_db`)
- `ITINERARY_SERVICE_URL`: URL of the Itinerary Service (default: `http://itinerary:5004`)
- `RABBITMQ_HOST`: RabbitMQ server address (default: `rabbitmq`)
- `RABBITMQ_PORT`: RabbitMQ server port (default: `5672`)

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5005
```
