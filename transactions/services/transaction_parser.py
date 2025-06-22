import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.utils.timezone import make_aware

from transactions.constants import SUPPORTED_CURRENCIES


def parse_transaction_row(row: dict) -> dict:
    try:
        transaction_id = uuid.UUID(row["transaction_id"])
        timestamp = make_aware(datetime.fromisoformat(row["timestamp"]))
        amount = Decimal(row["amount"])
        if amount <= 0:
            raise ValueError("Amount must be positive")

        currency = row["currency"]
        if currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")

        customer_id = uuid.UUID(row["customer_id"])
        product_id = uuid.UUID(row["product_id"])
        quantity = int(row["quantity"])
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

    except (KeyError, ValueError, InvalidOperation) as e:
        raise ValueError(f"Invalid row: {e}")

    return {
        "transaction_id": transaction_id,
        "timestamp": timestamp,
        "amount": amount,
        "currency": currency,
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
    }
