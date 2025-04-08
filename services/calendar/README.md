# Calendar Service

The Calendar Service manages group travel date coordination, allowing users to indicate their availability for group trips.

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
  "service": "calendar"
}
```

### Create Calendar

```
POST /api/calendars
```

Creates a new calendar for a group.

**Request:**
```json
{
  "group_id": 1,
  "start_date_range": "2023-07-01T00:00:00",
  "end_date_range": "2023-07-15T00:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "group_id": 1,
  "start_date_range": "2023-07-01T00:00:00",
  "end_date_range": "2023-07-15T00:00:00",
  "created_at": "2023-06-15T12:30:45"
}
```

### Get Group Calendar

```
GET /api/calendars/group/{group_id}
```

Retrieves the calendar and all user availabilities for a specific group.

**Response:**
```json
{
  "id": 1,
  "group_id": 1,
  "start_date_range": "2023-07-01T00:00:00",
  "end_date_range": "2023-07-15T00:00:00",
  "created_at": "2023-06-15T12:30:45",
  "user_availabilities": [
    {
      "id": 1,
      "calendar_id": 1,
      "user_id": 1,
      "available_dates": ["2023-07-05", "2023-07-06", "2023-07-07"],
      "created_at": "2023-06-16T14:20:00"
    },
    {
      "id": 2,
      "calendar_id": 1,
      "user_id": 2,
      "available_dates": ["2023-07-06", "2023-07-07", "2023-07-08"],
      "created_at": "2023-06-16T15:10:00"
    }
  ]
}
```

### Delete Group Calendar

```
DELETE /api/calendars/group/{group_id}
```

Deletes the calendar and all associated user availabilities for a specific group.

**Response:**
```json
{
  "message": "Calendar for group 1 deleted successfully"
}
```

### Get Calendar Availability

```
GET /api/calendars/{calendar_id}/availability
```

Retrieves all user availabilities for a specific calendar.

**Response:**
```json
{
  "calendar": {
    "id": 1,
    "group_id": 1,
    "start_date_range": "2023-07-01T00:00:00",
    "end_date_range": "2023-07-15T00:00:00",
    "created_at": "2023-06-15T12:30:45"
  },
  "availabilities": [
    {
      "id": 1,
      "calendar_id": 1,
      "user_id": 1,
      "available_dates": ["2023-07-05", "2023-07-06", "2023-07-07"],
      "created_at": "2023-06-16T14:20:00"
    },
    {
      "id": 2,
      "calendar_id": 1,
      "user_id": 2,
      "available_dates": ["2023-07-06", "2023-07-07", "2023-07-08"],
      "created_at": "2023-06-16T15:10:00"
    }
  ]
}
```

### Update Calendar Availability

```
POST /api/calendars/{calendar_id}/availability
```

Updates a user's availability for a specific calendar.

**Request:**
```json
{
  "user_id": 1,
  "available_dates": ["2023-07-08", "2023-07-09", "2023-07-10"]
}
```

**Response:**
```json
{
  "id": 1,
  "calendar_id": 1,
  "user_id": 1,
  "available_dates": ["2023-07-08", "2023-07-09", "2023-07-10"],
  "created_at": "2023-06-16T14:20:00",
  "updated_at": "2023-06-17T10:45:00"
}
```

## RabbitMQ Integration

The Calendar Service can consume messages from RabbitMQ to receive calendar-related events from other services.

## Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@calendar-db:5432/calendar_db`)
- `RABBITMQ_HOST`: RabbitMQ server address (default: `rabbitmq`)
- `RABBITMQ_PORT`: RabbitMQ server port (default: `5672`)

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5004
```
