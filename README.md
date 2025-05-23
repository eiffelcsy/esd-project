# ESD Trip Planner

A microservices-based travel planning application that enables users to create and manage trips, group travel, itineraries, expenses, and more.

## System Architecture

The application consists of the following microservices:

1. **User Service** (Port: 5001)
   - User registration and authentication
   - User profile management

2. **Recommendation Management Service** (Port: 5002)
   - AI-powered travel recommendations
   - Integration with OpenAI

3. **Group Management Service** (Port: 5003)
   - Create and manage travel groups
   - User invitation and joining features

4. **Calendar Service** (Port: 5004)
   - Group availability management
   - Date coordination for trips

5. **Trip Management Service** (Port: 5005)
   - Create and manage trip details
   - Coordinates with other services

6. **Itinerary Service** (Port: 5006)
   - Create detailed trip itineraries
   - Activity scheduling and management
   - Recommendation integration

7. **Expense Management Service** (Port: 5007)
   - Track and manage trip expenses
   - Interface with Finance service

8. **Finance Service** (Port: 5008)
   - Currency conversion
   - Expense calculation and splitting
   - Settlement planning

## Communication Patterns

- **REST APIs**: All services expose REST endpoints for direct interaction
- **RabbitMQ**: Used for asynchronous communication between services

## Getting Started

To run the application:

```bash
# Start all services
docker-compose up -d

# Monitor logs
docker-compose logs -f
```

See individual service README files for detailed API documentation and usage examples.
