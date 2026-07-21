from django.db import models


class UploadedFile(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    event_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.filename


class Event(models.Model):
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="events",
    )

    srcaddr = models.GenericIPAddressField(db_index=True)
    dstaddr = models.GenericIPAddressField(db_index=True)

    action = models.CharField(max_length=20, db_index=True)

    starttime = models.BigIntegerField(db_index=True)

    log_status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.action} | {self.srcaddr} -> {self.dstaddr}"