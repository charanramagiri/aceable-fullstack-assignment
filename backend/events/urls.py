from django.urls import path
from .api.health_views import health_check
from .api.upload_views import upload_files
from .api.search_views import search_test
from .views import parse_test

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("upload/", upload_files, name="upload-files"),
    path("parse-test/", parse_test),
    path("search-test/", search_test),
]
