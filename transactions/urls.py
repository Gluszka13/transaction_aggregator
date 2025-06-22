from django.urls import path
from transactions.views import (
    CSVUploadView,
    TransactionListView,
    TransactionDetailView,
    CustomerSummaryView,
    ProductSummaryView,
)

urlpatterns = [
    path("transactions/upload/", CSVUploadView.as_view(), name="transactions-upload"),
    path("transactions/", TransactionListView.as_view(), name="transactions-list"),
    path("transactions/<uuid:transaction_id>/", TransactionDetailView.as_view(), name="transactions-detail"),
    path("reports/customer-summary/<uuid:customer_id>/", CustomerSummaryView.as_view(), name="customer-summary"),
    path("reports/product-summary/<uuid:product_id>/", ProductSummaryView.as_view(), name="product-summary"),
]

