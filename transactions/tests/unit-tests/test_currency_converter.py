import pytest
from transactions.services.currency_converter import CurrencyConverter


def test_conversion_eur_to_pln():
    assert CurrencyConverter.to_pln(10, "EUR") == 43.0


def test_conversion_usd_to_pln():
    assert CurrencyConverter.to_pln(10, "USD") == 40.0


def test_conversion_pln_to_pln():
    assert CurrencyConverter.to_pln(10, "PLN") == 10.0


def test_invalid_currency():
    with pytest.raises(ValueError, match="No exchange rate"):
        CurrencyConverter.to_pln(10, "CHF")
