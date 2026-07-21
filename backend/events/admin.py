# Register your models here.
from django.contrib import admin

from .models import UploadedFile, Event


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filename",
        "uploaded_at",
        "event_count",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "action",
        "srcaddr",
        "dstaddr",
        "starttime",
    )

    search_fields = (
        "srcaddr",
        "dstaddr",
        "action",
    )