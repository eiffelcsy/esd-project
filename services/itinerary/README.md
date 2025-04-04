# Itinerary Service

The Itinerary Service is responsible for managing trip itineraries, including activities, schedules, and attraction recommendations.

## Features

- Create and manage trip itineraries
- Receive trip data from Trip Management Service via RabbitMQ
- Request and receive recommendations from Recommendation Management Service via RabbitMQ
- Store and retrieve itinerary data
- Generate calendar files (ICS) for trip itineraries

## Integration with Recommendation Management Service

The Itinerary Service integrates with the Recommendation Management Service to get personalized travel recommendations for trips. This integration uses asynchronous messaging via RabbitMQ.

### Communication via RabbitMQ

- When a new trip is created, the Itinerary Service sends a recommendation request to the `recommendation_requests` queue
- The Recommendation Management Service processes these requests and publishes responses to the `recommendation_responses` queue
- The Itinerary Service listens to the `recommendation_responses` queue and updates its local recommendation store

### Data Flow

1. User creates a trip in the Trip Management Service
2. Trip Management Service publishes a message to the `trip_details` queue
3. Itinerary Service receives the trip details and creates a new itinerary
4. Itinerary Service requests recommendations by publishing to the `recommendation_requests` queue
5. Recommendation Management Service processes the request and publishes results to `recommendation_responses`
6. Itinerary Service receives the recommendations and stores them

## Environment Variables

- `DATABASE_URL`: PostgreSQL database connection string
- `TRIP_MANAGEMENT_URL`: URL of the Trip Management Service
- `RABBITMQ_URL`: RabbitMQ connection URL

## API Endpoints

- `GET /api/itineraries`: Get all itineraries
- `GET /api/itineraries/<trip_id>`: Get itinerary by trip ID
- `POST /api/itineraries/<trip_id>/activities`: Add activity to itinerary
- `PUT /api/itineraries/<trip_id>/activities/<activity_id>`: Update activity
- `DELETE /api/itineraries/<trip_id>/activities/<activity_id>`: Delete activity
- `GET /api/itineraries/<trip_id>/recommendations`: Get recommendations for trip
- `GET /api/itineraries/<trip_id>/calendar`: Get calendar file for itinerary

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- RabbitMQ

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Run the service: `python app.py`

### Docker

```bash
docker build -t itinerary-service .
docker run -p 5006:5006 itinerary-service
```
