from datetime import datetime
from uuid import UUID

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination

from django.conf import settings
from django.db.models import Max, Sum
from django.utils.timezone import make_aware

from transactions.tasks import import_csv_task
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from transactions.services.currency_converter import CurrencyConverter


class CSVUploadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.headers.get("Authorization")
        if token != f"Token {settings.API_TOKEN}":
            return Response({"detail": "Unauthorized"}, status=401)

        if "file" not in request.FILES:
            return Response({"detail": "Missing file"}, status=400)

        file = request.FILES["file"]
        content = file.read().decode("utf-8")
        import_csv_task.delay(content, file.name)

        return Response({"detail": "Import started"}, status=202)


class TransactionPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class TransactionListView(ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = TransactionPagination

    def get_queryset(self):
        qs = Transaction.objects.all()
        params = self.request.query_params

        if customer_id := params.get("customer_id"):
            qs = qs.filter(customer_id=customer_id)
        if product_id := params.get("product_id"):
            qs = qs.filter(product_id=product_id)

        return qs.order_by("timestamp")


class TransactionDetailView(RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "transaction_id"


class CustomerSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, customer_id):
        qs = Transaction.objects.filter(customer_id=customer_id)

        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        if date_from:
            try:
                qs = qs.filter(timestamp__gte=make_aware(datetime.fromisoformat(date_from)))
            except ValueError:
                return Response({"detail": "Invalid date_from"}, status=400)

        if date_to:
            try:
                qs = qs.filter(timestamp__lte=make_aware(datetime.fromisoformat(date_to)))
            except ValueError:
                return Response({"detail": "Invalid date_to"}, status=400)

        if not qs.exists():
            return Response({
                "total_spent_pln": 0.0,
                "unique_products_count": 0,
                "last_transaction_date": None,
            })

        converter = CurrencyConverter()
        total_spent = sum(converter.to_pln(tx.amount, tx.currency) for tx in qs)
        unique_products = qs.values("product_id").distinct().count()
        last_transaction = qs.aggregate(last=Max("timestamp"))["last"]

        return Response({
            "total_spent_pln": round(total_spent, 2),
            "unique_products_count": unique_products,
            "last_transaction_date": last_transaction,
        })


class ProductSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        qs = Transaction.objects.filter(product_id=product_id)

        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        if date_from:
            try:
                qs = qs.filter(timestamp__gte=make_aware(datetime.fromisoformat(date_from)))
            except ValueError:
                return Response({"detail": "Invalid date_from"}, status=400)

        if date_to:
            try:
                qs = qs.filter(timestamp__lte=make_aware(datetime.fromisoformat(date_to)))
            except ValueError:
                return Response({"detail": "Invalid date_to"}, status=400)

        if not qs.exists():
            return Response({
                "total_quantity_sold": 0,
                "total_revenue_pln": 0.0,
                "unique_customers_count": 0,
            })

        total_quantity = qs.aggregate(qty=Sum("quantity"))["qty"]
        converter = CurrencyConverter()
        total_revenue = sum(converter.to_pln(tx.amount, tx.currency) for tx in qs)
        unique_customers = qs.values("customer_id").distinct().count()

        return Response({
            "total_quantity_sold": total_quantity,
            "total_revenue_pln": round(total_revenue, 2),
            "unique_customers_count": unique_customers,
        })

