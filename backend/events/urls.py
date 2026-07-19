from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("upload/", views.upload_files, name="upload-files"),
    path("parse-test/", views.parse_test),
]