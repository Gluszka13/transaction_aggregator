from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from transactions.tasks import import_csv_task


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
