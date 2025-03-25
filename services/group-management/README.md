# Group Management Service

This is a composite microservice that orchestrates the creation of groups by coordinating between the User, Group, and Calendar microservices.

## Functionality

The service handles the following workflow:

1. Receives a group creation request with details (name, description, creator, users, date ranges)
2. Validates the creator's user ID with the User service
3. Creates a group via the Group service
4. Sets up a calendar for the group via the Calendar service
5. Tracks the status of each group creation request

## API Endpoints

### Create a Group

```
POST /api/groups
```

**Request Body:**

```json
{
  "name": "Trip to Japan",
  "description": "A two-week trip to Japan",
  "createdBy": 123, 
  "users": [123], 
  "startDateRange": "2023-10-01T00:00:00",
  "endDateRange": "2023-10-14T23:59:59"
}
```

**Response (Success):**

```json
{
  "id": 456,
  "name": "Trip to Japan",
  "description": "A two-week trip to Japan",
  "created_by": 123,
  "users": [123],
  "calendar": {
    "id": 789,
    "group_id": 456,
    "start_date_range": "2023-10-01T00:00:00",
    "end_date_range": "2023-10-14T23:59:59" 
  },
  "status": "completed"
}
```

### Get All Group Requests

```
GET /api/groups/requests
```

Returns a list of all group creation requests with their status.

### Get a Specific Group Request

```
GET /api/groups/requests/{request_id}
```

Returns details about a specific group creation request.

## Configuration

The service requires the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `USER_SERVICE_URL`: URL of the User microservice
- `GROUP_SERVICE_URL`: URL of the Group microservice
- `CALENDAR_SERVICE_URL`: URL of the Calendar microservice
- `PORT`: Port to run the service on (default: 5003)

## Running the Service

### Using Docker

```bash
docker build -t group-management .
docker run -p 5003:5003 --env-file .env group-management
```

### Using Docker Compose

Add the service to your docker-compose.yml file.

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (see .env.example)

3. Run the service:
   ```bash
   python app.py
   ```
