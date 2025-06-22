import csv
import io
import logging
from django.db import transaction, IntegrityError
from transactions.services.transaction_parser import parse_transaction_row
from transactions.models import Transaction

logger = logging.getLogger(__name__)


def import_csv_from_string(content: str) -> dict:
    """
    Import transactions from CSV content (string).
    Used by Celery.
    """
    return _import_from_reader(csv.DictReader(io.StringIO(content)))


def import_csv_file(file_path: str) -> dict:
    """
    Import transactions from a CSV file path.
    Used in tests and scripts.
    """
    with open(file_path, newline='') as f:
        return _import_from_reader(csv.DictReader(f))


def _import_from_reader(reader: csv.DictReader) -> dict:
    success_count = 0
    error_rows = []

    for i, row in enumerate(reader, start=1):
        try:
            parsed = parse_transaction_row(row)
            with transaction.atomic():
                Transaction.objects.create(**parsed)
            success_count += 1
        except (ValueError, IntegrityError) as e:
            error_rows.append((i, str(e)))

    logger.debug("CSV import complete: %s", {"imported": success_count, "errors": error_rows})
    return {"imported": success_count, "errors": error_rows}

