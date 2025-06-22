import os
from decimal import Decimal
from pathlib import Path

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.conf import settings

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
    import_csv_file(csv_path)


def test_customer_report(client, preload_report_data):
    response = client.get(CUSTOMER_REPORT_URL(CUSTOMER_ID), HTTP_AUTHORIZATION=f"Token {TOKEN}")
    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["total_spent_pln"])) == Decimal("538.45")  # 100 + 40 + 21.5 + 200 + 60 + 123.45
    assert data["unique_products_count"] == 2
    assert data["last_transaction_date"].startswith("2025-06-01")


def test_customer_report_with_date_filter(client, preload_report_data):
    response = client.get(
        CUSTOMER_REPORT_URL(CUSTOMER_ID) + "?date_from=2025-01-01&date_to=2025-01-31",
        HTTP_AUTHORIZATION=f"Token {TOKEN}"
    )
    assert response.status_code == 200
    data = response.json()
    # 100 (PLN) + 10*4 = 40 (USD) + 5*4.3 = 21.5 (EUR) + 200 (PLN)
    assert Decimal(str(data["total_spent_pln"])) == Decimal("361.5")
    assert data["unique_products_count"] == 2
    assert data["last_transaction_date"].startswith("2025-01-05")


def test_product_report(client, preload_report_data):
    response = client.get(PRODUCT_REPORT_URL(PRODUCT_ID), HTTP_AUTHORIZATION=f"Token {TOKEN}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_quantity_sold"] == 16  # 5+3+2+6
    assert Decimal(str(data["total_revenue_pln"])) == Decimal("221.5")  # 100 + 40 + 21.5 + 60
    assert data["unique_customers_count"] == 1


def test_product_report_with_date_filter(client, preload_report_data):
    response = client.get(
        PRODUCT_REPORT_URL(PRODUCT_ID) + "?date_from=2025-03-01&date_to=2025-03-31",
        HTTP_AUTHORIZATION=f"Token {TOKEN}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_quantity_sold"] == 6
    assert Decimal(str(data["total_revenue_pln"])) == Decimal("60.0")
    assert data["unique_customers_count"] == 1

