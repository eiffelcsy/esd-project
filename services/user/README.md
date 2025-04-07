# User Service

The User Service handles user authentication, registration, profile management, and search functionality.

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
  "service": "user"
}
```

### User Registration

```
POST /api/users/register
```

Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture": "https://example.com/profile.jpg"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile_picture": "https://example.com/profile.jpg"
  },
  "user_id": 1
}
```

### User Login

```
POST /api/users/login
```

Authenticate a user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile_picture": "https://example.com/profile.jpg"
  },
  "user_id": 1
}
```

### Get User Profile

```
GET /api/users/profile/{user_id}
```

Retrieve detailed user profile information.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture": "https://example.com/profile.jpg"
}
```

### Update User Profile

```
PUT /api/users/profile/{user_id}
```

Update a user's profile.

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "profile_picture": "https://example.com/new-profile.jpg",
  "password": "new-password123"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "profile_picture": "https://example.com/new-profile.jpg"
  }
}
```

### Get Public User Profile

```
GET /api/users/{user_id}
```

Retrieve public user profile information.

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Smith",
  "profile_picture": "https://example.com/new-profile.jpg"
}
```

### Search Users

```
GET /api/users/search?q={query}
```

Search for users by email address.

**Response:**
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Smith",
    "profile_picture": "https://example.com/profile.jpg"
  },
  {
    "id": 2,
    "first_name": "Jane",
    "last_name": "Doe",
    "profile_picture": "https://example.com/profile2.jpg"
  }
]
```

## Required Environment Variables

- `DATABASE_URL`: Connection string for PostgreSQL database (default: `postgresql://postgres:postgres@user-db:5432/user_db`)

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5001
```

## Features

- User registration with validation
- User authentication with JWT
- User profile management
- User search functionality

## API Endpoints

### Authentication

- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - User login

### User Profile

- `GET /api/users/profile` - Get current user profile (authenticated)
- `PUT /api/users/profile` - Update user profile (authenticated)
- `GET /api/users/<user_id>` - Get public user profile by ID
- `GET /api/users/search?q=<query>` - Search users by username

## Running the Service

### Using Docker

```bash
docker build -t user-service .
docker run -p 5001:5001 user-service
```

### Local Development

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/user_db
export JWT_SECRET_KEY=your-secret-key
```

3. Run the application:
```bash
python app.py
```

## Database Schema

### Users Table

- id: Primary key
- username: Unique username
- email: Unique email address
- password_hash: Hashed password
- first_name: User's first name
- last_name: User's last name
- profile_picture: URL to profile picture
- created_at: Account creation timestamp
- updated_at: Last update timestamp
