# Finance Service

The Finance Service manages financial aspects of trips, including expense tracking, currency conversion, and expense settlement between group members.

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
  "service": "finance"
}
```

### Get Currency Exchange Rates

```
GET /api/finance/rates?base={base_currency}&symbols={target_currencies}
```

Retrieves exchange rates for a base currency.

**Parameters:**
- `base` (optional): Base currency (default: SGD)
- `symbols` (optional): Comma-separated list of target currencies

**Response:**
```json
{
  "result": "success",
  "rates": {
    "USD": 0.74,
    "EUR": 0.68,
    "GBP": 0.58,
    "JPY": 110.42,
    "AUD": 1.11
  }
}
```

### Convert Currency

```
GET /api/finance/convert/{from_currency}/{to_currency}/{amount}
```

Converts an amount from one currency to another.

**Response:**
```json
{
  "from": "SGD",
  "to": "USD",
  "original_amount": 100,
  "converted_amount": 74,
  "rate": 0.74
}
```

### Get Trip Expenses

```
GET /api/finance/expenses/{trip_id}
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

### Calculate Trip Expenses

```
GET /api/finance/calculate/{trip_id}?base={base_currency}
```

Calculates total expenses and settlement plan for a trip.

**Parameters:**
- `base` (optional): Base currency for calculations (default: SGD)

**Response:**
```json
{
  "trip_id": "123",
  "total_amount": 75.75,
  "currency": "EUR",
  "expenses": [
    {
      "id": 1,
      "user_id": 1,
      "payee_id": 2,
      "amount": 50.75,
      "currency": "EUR",
      "description": "Dinner at Le Bistro"
    },
    {
      "id": 2,
      "user_id": 2,
      "payee_id": null,
      "amount": 25.00,
      "currency": "EUR",
      "description": "Museum tickets"
    }
  ],
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "balance": 25.75
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "balance": -25.75
    }
  ],
  "settlements": [
    {
      "from": 2,
      "from_name": "Jane Smith",
      "to": 1,
      "to_name": "John Doe",
      "amount": 25.75,
      "currency": "EUR"
    }
  ]
}
```

### Add Expense

```
POST /api/finance/{trip_id}/add
```

Adds a new expense to a trip.

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
  "expense_id": 1,
  "status": "recorded",
  "trip_id": "123",
  "amount": 50.75,
  "currency": "EUR"
}
```

### Get Readiness Status

```
GET /api/finance/readiness/{trip_id}
```

Retrieves the readiness status of users for a trip's expense settlement.

**Response:**
```json
{
  "trip_id": "123",
  "ready_users": [
    {
      "user_id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "is_ready": true
    }
  ],
  "not_ready_users": [
    {
      "user_id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "is_ready": false
    }
  ],
  "total_users": 2,
  "ready_count": 1,
  "all_ready": false
}
```

### Update Readiness Status

```
PUT /api/finance/readiness/{trip_id}/{user_id}
```

Updates a user's readiness status for expense settlement.

**Request:**
```json
{
  "is_ready": true,
  "name": "Jane Smith",
  "email": "jane@example.com"
}
```

**Response:**
```json
{
  "message": "User 2 readiness status updated to ready",
  "user_id": 2,
  "trip_id": "123",
  "is_ready": true,
  "all_ready": true
}
```

## External API Integration

The Finance Service integrates with:

- **ExchangeRate API**: For real-time currency conversion rates
- **Email Service**: For sending settlement notifications

## Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@finance-db:5432/finance_db`)
- `EXCHANGERATE_API_KEY`: API key for ExchangeRate API
- `EMAIL_API_KEY`: API key for email service
- `EMAIL_SENDER`: Sender email address

## Development

To run the service locally:

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5008
```
