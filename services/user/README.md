# User Service

This microservice handles user authentication, registration, and profile management for the trip planning application.

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
