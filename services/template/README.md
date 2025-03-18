# Template Microservice

This is a template microservice that provides CRUD operations via a RESTful API using Flask. It can be used as a starting point for creating new microservices.

## Features

- RESTful API with CRUD operations
- Flask-SQLAlchemy for ORM
- Docker containerization
- Health check endpoint

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Service health check |
| GET | /api/items | Get all items |
| GET | /api/items/{id} | Get a specific item by ID |
| POST | /api/items | Create a new item |
| PUT | /api/items/{id} | Update an existing item |
| DELETE | /api/items/{id} | Delete an item |

## Running the Service

### Using Docker

```bash
docker build -t template-service .
docker run -p 5000:5000 template-service
```

### Using Docker Compose

```bash
docker-compose up template
```

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python app.py
```

## Environment Variables

- `DATABASE_URL`: URL for the database connection (default: sqlite:///template.db) 