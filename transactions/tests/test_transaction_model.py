from transactions.models import Transaction


def test_transaction_creation(db):
    t = Transaction.objects.create()
    assert t.id is not None
