import csv
from transactions.services.transaction_parser import parse_transaction_row
from transactions.models import Transaction
from django.db import IntegrityError


def import_csv_file(file_path: str) -> dict:
    success_count = 0
    error_rows = []

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, start=1):
            try:
                parsed = parse_transaction_row(row)
                Transaction.objects.create(**parsed)
                success_count += 1
            except (ValueError, IntegrityError) as e:
                error_rows.append((i, str(e)))

    return {"imported": success_count, "errors": error_rows}
