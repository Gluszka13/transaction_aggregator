from django.db import models
from .constants import CURRENCY_CHOICES


class Transaction(models.Model):
    transaction_id = models.UUIDField(unique=True)
    timestamp = models.DateTimeField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    customer_id = models.UUIDField(db_index=True)
    product_id = models.UUIDField(db_index=True)
    quantity = models.PositiveIntegerField()
