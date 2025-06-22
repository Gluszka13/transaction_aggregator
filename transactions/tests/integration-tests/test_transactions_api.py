import os
import pytest
from pathlib import Path
from django.urls import reverse
from rest_framework.test import APIClient
from transactions.services.csv_importer import import_csv_file

TOKEN = os.getenv("API_TOKEN")
LIST_URL = reverse("transactions-list")
DETAIL_URL = lambda pk: reverse("transactions-detail", args=[pk])

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def preload_transactions():
    csv_path = Path(__file__).parent / "data" / "test_transactions_full.csv"
    import_csv_file(csv_path)


def test_list_all_transactions(client, preload_transactions):
    response = client.get(LIST_URL, HTTP_AUTHORIZATION=f"Token {TOKEN}")
    assert response.status_code == 200
    assert "results" in response.data
    assert response.data["count"] == 12


def test_filter_by_customer(client, preload_transactions):
    customer_id = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    response = client.get(f"{LIST_URL}?customer_id={customer_id}", HTTP_AUTHORIZATION=f"Token {TOKEN}")
    assert response.status_code == 200
    assert len(response.data["results"]) == 4
    for item in response.data["results"]:
        assert item["customer_id"] == customer_id


def test_filter_by_product(client, preload_transactions):
    product_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    response = client.get(f"{LIST_URL}?product_id={product_id}", HTTP_AUTHORIZATION=f"Token {TOKEN}")
    assert response.status_code == 200
    assert len(response.data["results"]) == 4
    for item in response.data["results"]:
        assert item["product_id"] == product_id


def test_filter_pagination_combined(client, preload_transactions):
    customer_id = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    response = client.get(
        f"{LIST_URL}?customer_id={customer_id}&page=1&page_size=2",
        HTTP_AUTHORIZATION=f"Token {TOKEN}"
    )
    assert response.status_code == 200
    assert len(response.data["results"]) == 2


def test_transaction_retrieve(client, preload_transactions):
    transaction_id = "4e655a43-40f0-4555-9532-500077d0c54e"
    response = client.get(DETAIL_URL(transaction_id), HTTP_AUTHORIZATION=f"Token {TOKEN}")
    assert response.status_code == 200
    assert response.data["transaction_id"] == transaction_id

