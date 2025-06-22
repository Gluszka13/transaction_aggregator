import pytest
from transactions.services.transaction_parser import parse_transaction_row

valid_row = {
    "transaction_id": "9bfa6a49-9f25-4f42-8963-df50b9bb0e48",
    "timestamp": "2025-01-01T12:00:00",
    "amount": "100.50",
    "currency": "EUR",
    "customer_id": "6b36c37d-8788-4025-89f1-1e3df07cc1cc",
    "product_id": "8799fbc9-46db-4f57-974d-1a11b41483b5",
    "quantity": "2",
}


def test_valid_row():
    data = parse_transaction_row(valid_row)
    assert data["currency"] == "EUR"
    assert data["quantity"] == 2


def test_invalid_currency():
    row = valid_row.copy()
    row["currency"] = "CHF"
    with pytest.raises(ValueError, match="Unsupported currency"):
        parse_transaction_row(row)


def test_invalid_quantity_zero():
    row = valid_row.copy()
    row["quantity"] = "0"
    with pytest.raises(ValueError, match="Quantity must be positive"):
        parse_transaction_row(row)


def test_invalid_quantity_negative():
    row = valid_row.copy()
    row["quantity"] = "-5"
    with pytest.raises(ValueError, match="Quantity must be positive"):
        parse_transaction_row(row)


def test_invalid_amount_zero():
    row = valid_row.copy()
    row["amount"] = "0"
    with pytest.raises(ValueError, match="Amount must be positive"):
        parse_transaction_row(row)


def test_invalid_amount_negative():
    row = valid_row.copy()
    row["amount"] = "-10.50"
    with pytest.raises(ValueError, match="Amount must be positive"):
        parse_transaction_row(row)


def test_missing_field():
    row = valid_row.copy()
    del row["amount"]
    with pytest.raises(ValueError, match="Invalid row"):
        parse_transaction_row(row)
