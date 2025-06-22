import os
import pytest
from decimal import Decimal
from pathlib import Path
from rest_framework.test import APIClient
from django.urls import reverse
from transactions.services.csv_importer import import_csv_file

TOKEN = os.getenv("API_TOKEN")

CUSTOMER_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PRODUCT_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"

CUSTOMER_REPORT_URL = lambda cid: reverse("customer-summary", args=[cid])
PRODUCT_REPORT_URL = lambda pid: reverse("product-summary", args=[pid])

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def preload_report_data():
    csv_path = Path(__file__).parent / "data" / "test_transactions_reports.csv"
    result = import_csv_file(csv_path)
    assert result['imported'] == 7, result['errors']


def test_customer_report(client, preload_report_data):
    response = client.get(
        CUSTOMER_REPORT_URL(CUSTOMER_ID), HTTP_AUTHORIZATION=f"Token {TOKEN}"
    )
    assert response.status_code == 200
    data = response.data
    assert data["total_spent_pln"] == Decimal("1090.00")
    assert data["unique_products_count"] == 2
    assert "last_transaction_date" in data


def test_customer_report_with_date_filter(client, preload_report_data):
    response = client.get(
        CUSTOMER_REPORT_URL(CUSTOMER_ID) + "?date_from=2025-03-01&date_to=2025-03-31",
        HTTP_AUTHORIZATION=f"Token {TOKEN}",
    )
    assert response.status_code == 200
    data = response.data
    assert data["total_spent_pln"] == Decimal("260.00")
    assert data["unique_products_count"] == 1


def test_product_report(client, preload_report_data):
    response = client.get(
        PRODUCT_REPORT_URL(PRODUCT_ID), HTTP_AUTHORIZATION=f"Token {TOKEN}"
    )
    assert response.status_code == 200
    data = response.data
    assert data["total_quantity_sold"] == 14
    assert data["total_revenue_pln"] == Decimal("1212.50")
    assert data["unique_customers_count"] == 2


def test_product_report_with_date_filter(client, preload_report_data):
    response = client.get(
        PRODUCT_REPORT_URL(PRODUCT_ID) + "?date_from=2025-03-01&date_to=2025-03-31",
        HTTP_AUTHORIZATION=f"Token {TOKEN}",
    )
    assert response.status_code == 200
    data = response.data
    assert data["total_quantity_sold"] == 6
    assert data["total_revenue_pln"] == Decimal("260.00")
