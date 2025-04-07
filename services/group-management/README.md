# Group Management Service

The Group Management Service handles creation and management of travel groups, enabling users to plan trips together.

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
  "service": "group-management"
}
```

### Create Group

```
POST /api/groups
```

Creates a new travel group and initializes a calendar for the group.

**Request:**
```json
{
  "name": "Europe Trip 2023",
  "description": "Summer trip through Europe",
  "createdBy": 1,
  "users": [2, 3, 4],
  "startDateRange": "2023-07-01T00:00:00",
  "endDateRange": "2023-07-15T00:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Europe Trip 2023",
  "description": "Summer trip through Europe",
  "created_by": 1,
  "calendar": {
    "id": 1,
    "group_id": 1,
    "start_date_range": "2023-07-01T00:00:00",
    "end_date_range": "2023-07-15T00:00:00"
  },
  "status": "completed",
  "invited_users": [2, 3, 4],
  "active_users": [1]
}
```

### Join Group

```
POST /api/groups/{group_id}/join
```

Allows an invited user to join a group.

**Request:**
```json
{
  "user_id": 2
}
```

**Response:**
```json
{
  "message": "User 2 successfully joined group 1",
  "group_id": 1,
  "user_id": 2,
  "joined_users": [1, 2]
}
```

### Get Group

```
GET /api/groups/{group_id}
```

Retrieves details about a specific group.

**Response:**
```json
{
  "id": 1,
  "name": "Europe Trip 2023",
  "description": "Summer trip through Europe",
  "created_by": 1,
  "members": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "profile_picture": "https://example.com/profile1.jpg"
    },
    {
      "id": 2,
      "first_name": "Jane",
      "last_name": "Smith",
      "profile_picture": "https://example.com/profile2.jpg"
    }
  ],
  "invited_users": [3, 4]
}
```

### Get User Groups

```
GET /api/users/{user_id}/groups
```

Retrieves all groups a user is a member of.

**Response:**
```json
{
  "active_groups": [
    {
      "id": 1,
      "name": "Europe Trip 2023",
      "description": "Summer trip through Europe",
      "created_by": 1,
      "member_count": 2
    }
  ],
  "invited_groups": [
    {
      "id": 2,
      "name": "Asia Trip 2024",
      "description": "Spring trip to Japan",
      "created_by": 3,
      "member_count": 3
    }
  ]
}
```

### Invite User to Group

```
POST /api/groups/{group_id}/invite
```

Invites a user to join a group.

**Request:**
```json
{
  "user_id": 5
}
```

**Response:**
```json
{
  "message": "User 5 invited to group 1",
  "group_id": 1,
  "invited_user": 5
}
```

### Remove User from Group

```
DELETE /api/groups/{group_id}/users/{user_id}
```

Removes a user from a group.

**Response:**
```json
{
  "message": "User 2 removed from group 1",
  "group_id": 1,
  "user_id": 2
}
```

### Delete Group

```
DELETE /api/groups/{group_id}
```

Deletes a group and all associated resources.

**Response:**
```json
{
  "message": "Group 1 deleted successfully",
  "group_id": 1
}
```

## Service Integration

The Group Management Service integrates with:

- **User Service**: To validate users and retrieve user details
- **Calendar Service**: To create and manage group availability calendars

## Required Environment Variables

- `DATABASE_URL`: Connection string for PostgreSQL database (default: `postgresql://postgres:postgres@grouprequest-db:5432/grouprequest_db`)
- `USER_SERVICE_URL`: URL of the User Service (default: `http://user:5001`)
- `CALENDAR_SERVICE_URL`: URL of the Calendar Service (default: `http://calendar:5004`)

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5003
```
