# Expense Management Service

The Expense Management Service provides an interface for tracking and managing travel expenses. It acts as a proxy to the Finance Service, providing a simplified API for expense-related operations.

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
  "service": "expense-management"
}
```

### Add Expense

```
POST /api/expenses
```

Processes and forwards expense data to the Finance Service.

**Request:**
```json
{
  "trip_id": "123",
  "user_id": 1,
  "date": "2023-07-05",
  "location": "Paris, France",
  "amount": 50.75,
  "base_currency": "EUR",
  "description": "Dinner at Le Bistro",
  "is_paid": true,
  "category": "food",
  "payee_id": 2
}
```

**Response:**
```json
{
  "result": {
    "expense_id": 1,
    "status": "recorded",
    "trip_id": "123",
    "amount": 50.75,
    "currency": "EUR"
  },
  "message": "Expense successfully processed."
}
```

### Get Trip Expenses

```
GET /api/expenses/{trip_id}
```

Retrieves all expenses for a specific trip without calculations.

**Response:**
```json
{
  "trip_id": "123",
  "expenses": [
    {
      "id": 1,
      "trip_id": "123",
      "user_id": 1,
      "payee_id": 2,
      "date": "2023-07-05",
      "location": "Paris, France",
      "amount": 50.75,
      "base_currency": "EUR",
      "description": "Dinner at Le Bistro",
      "is_paid": true,
      "category": "food",
      "created_at": "2023-07-05T20:30:45"
    },
    {
      "id": 2,
      "trip_id": "123",
      "user_id": 2,
      "payee_id": null,
      "date": "2023-07-06",
      "location": "Paris, France",
      "amount": 25.00,
      "base_currency": "EUR",
      "description": "Museum tickets",
      "is_paid": true,
      "category": "entertainment",
      "created_at": "2023-07-06T10:15:30"
    }
  ]
}
```

### Convert Currency

```
GET /api/expenses/convert/{from_currency}/{to_currency}/{amount}
```

Converts an amount from one currency to another using the Finance Service.

**Response:**
```json
{
  "from": "EUR",
  "to": "USD",
  "original_amount": 50.75,
  "converted_amount": 55.32,
  "rate": 1.09
}
```

## Service Integration

The Expense Management Service acts as a proxy to the Finance Service for expense-related operations. It simplifies the API and provides a more focused interface for the frontend.

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5007
```

## Dependencies

- **Finance Service**: For expense processing, currency conversion, and data storage 