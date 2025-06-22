# Transaction Importer API

A Django REST API for uploading and processing transaction data from CSV files. Includes endpoints for listing and retrieving transactions, as well as generating customer and product summary reports.

## Features

- CSV file import via background Celery task
- Token-based authentication for all endpoints
- Transaction listing, filtering, pagination
- Detailed transaction view
- Customer and product report summaries
- Currency conversion support (EUR/USD to PLN)
- Unit and integration test coverage

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Setup

```bash
docker-compose up --build
```

Once the services are up, the API will be available at:

```
http://localhost:8000/api/
```

The default token is:

```
Token secret123
```

## Usage

### Importing Transactions

Upload a CSV file:

```bash
curl -X POST http://localhost:8000/api/transactions/upload/ \
  -H "Authorization: Token secret123" \
  -F "file=@transactions/tests/integration-tests/data/test_transactions_full.csv"
```

### Watching Celery logs

To observe import progress:

```bash
docker-compose logs -f celery
```

You’ll see logs indicating successful imports or validation errors per row.

---

### List Transactions

```bash
curl -H "Authorization: Token secret123" http://localhost:8000/api/transactions/
```

### Retrieve Single Transaction

```bash
curl -H "Authorization: Token secret123" http://localhost:8000/api/transactions/<transaction_id>/
```

---

### Customer Summary Report

```bash
curl -H "Authorization: Token secret123" \
  http://localhost:8000/api/reports/customer-summary/<customer_id>/?date_from=2025-01-01&date_to=2025-12-31
```

### Product Summary Report

```bash
curl -H "Authorization: Token secret123" \
  http://localhost:8000/api/reports/product-summary/<product_id>/?date_from=2025-01-01&date_to=2025-12-31
```

---

## Running Tests

### Unit Tests

```bash
pytest transactions/tests/unit-tests/
```

### Integration Tests

```bash
pytest transactions/tests/integration-tests/
```

## Notes

- All invalid rows in CSV are reported individually, but don’t block processing.
- Conversion rates are fixed:
  - 1 EUR = 4.3 PLN
  - 1 USD = 4.0 PLN
