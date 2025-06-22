from django.urls import path
from .views import CSVUploadView

urlpatterns = [
    path("transactions/upload/", CSVUploadView.as_view()),
]
