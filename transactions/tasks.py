import logging
import csv
import io
from celery import shared_task
from transactions.services.transaction_parser import parse_transaction_row
from transactions.models import Transaction
from django.db import IntegrityError

logger = logging.getLogger(__name__)


@shared_task
def import_csv_task(content: str, filename: str = "upload.csv"):
    success_count = 0
    error_rows = []

    reader = csv.DictReader(io.StringIO(content))
    for i, row in enumerate(reader, start=1):
        try:
            parsed = parse_transaction_row(row)
            Transaction.objects.create(**parsed)
            success_count += 1
        except (ValueError, IntegrityError) as e:
            error_rows.append((i, str(e)))

    logger.debug(
        "CSV import complete: %s", {"imported": success_count, "errors": error_rows}
    )
    return {"imported": success_count, "errors": error_rows}
