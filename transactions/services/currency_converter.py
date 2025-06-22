from decimal import Decimal
from transactions.constants import EXCHANGE_RATES


class CurrencyConverter:
    @classmethod
    def to_pln(cls, amount, currency):
        rate = EXCHANGE_RATES.get(currency)
        if rate is None:
            raise ValueError(f"No exchange rate for {currency}")
        return round(amount * Decimal(str(rate)), 2)

