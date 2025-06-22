import os
import pytest
from pathlib import Path
from rest_framework.test import APIClient
from django.urls import reverse
from transactions.services.csv_importer import import_csv_file
from transactions.models import Transaction

TOKEN = os.getenv("API_TOKEN")

pytestmark = pytest.mark.django_db

UPLOAD_URL = reverse("transactions-upload")


@pytest.fixture
def client():
    return APIClient()


def test_import_valid_and_invalid_mixed():
    csv_path = Path(__file__).parent / "data" / "test_transactions_upload_mixed.csv"
    result = import_csv_file(csv_path)

    assert result["imported"] == 2
    assert len(result["errors"]) == 3


def test_import_duplicates_are_skipped():
    csv_path = Path(__file__).parent / "data" / "test_transactions_upload_mixed.csv"
    import_csv_file(csv_path)
    count_before = Transaction.objects.count()
    import_csv_file(csv_path)
    count_after = Transaction.objects.count()

    assert count_after == count_before


def test_import_totally_invalid_file(tmp_path):
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("this is not csv at all")

    result = import_csv_file(bad_file)
    assert result["imported"] == 0
    assert len(result["errors"]) == 0
