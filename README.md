# Transaction Aggregator

## Overview

A REST API for importing and aggregating transaction data from CSV files. It provides endpoints for listing and retrieving transactions, as well as generating summary reports per customer or product. Currency conversion is applied to compute total amounts in PLN.

The system supports asynchronous CSV import using Celery, with Redis as a broker and PostgreSQL as the main datastore.

---

## Features

- Import transactions from CSV (async via Celery)
- Duplicate transaction detection (based on `transaction_id`)
- Token-based authentication
- Paginated and filterable transaction list
- Customer and product summary reports with date range support
- Conversion of USD/EUR amounts to PLN using fixed rates
- Logging of import results and API errors
- Indexed fields for optimized filtering by `customer_id` and `product_id`

---

## Technologies

- Python 3.10
- Django 4.x
- Celery
- PostgreSQL
- Redis
- Docker & Docker Compose
- pytest

---

## Setup

### `.env` example

```env
POSTGRES_DB=mydb
POSTGRES_USER=user
POSTGRES_PASSWORD=password

DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

API_TOKEN=secret123
CELERY_BROKER_URL=redis://redis:6379/0
```

---

## Running the App

Start all services with:

```bash
docker-compose up --build
```

Services:
- Django API (http://localhost:8000)
- PostgreSQL
- Redis
- Celery worker

---

## Running Tests

Run unit and integration tests via:

```bash
docker-compose run web pytest
```

### Unit tests
- `test_currency_converter.py`
- `test_transaction_parser.py`

### Integration tests
- `test_transactions_api.py`: listing, filtering, retrieval
- `test_reports_api.py`: customer/product reports
- `test_upload_api.py`: CSV import scenarios

> All integration tests rely on the same `csv_import_file(...)` logic that Celery uses to import data.

---

## Manual CSV Upload via CURL

```bash
curl -X POST http://localhost:8000/api/transactions/upload/ \
  -H "Authorization: Token secret123" \
  -F "file=@transactions/tests/integration-tests/data/test_transactions_reports.csv"
```

Watch Celery logs:

```bash
docker-compose logs -f celery
```

---

## API Endpoints

| Method | Endpoint                                                       | Description                       |
|--------|----------------------------------------------------------------|-----------------------------------|
| GET    | `/api/ping/`                                                   | Health check                      |
| POST   | `/api/transactions/upload/`                                    | Upload CSV (auth required)        |
| GET    | `/api/transactions/`                                           | List transactions (filters/paging)|
| GET    | `/api/transactions/<uuid:transaction_id>/`                    | Retrieve transaction by ID        |
| GET    | `/api/reports/customer-summary/<str:customer_id>/`           | Customer summary report           |
| GET    | `/api/reports/product-summary/<str:product_id>/`             | Product summary report            |

All endpoints require the header:

```
Authorization: Token secret123
```

---

## Notes

- Currency conversion rates are fixed (`EUR → 4.3`, `USD → 4.0`) and configured in `constants.py`.
- `transaction_id` is enforced as unique – duplicate rows are skipped during import.
- Invalid rows (e.g. malformed dates, missing fields) are logged during import.
- Indexed fields (`customer_id`, `product_id`, `timestamp`) ensure efficient query performance.
- All logs (including errors and Celery import results) are available via Django and Celery logs.

