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

    serialno = models.PositiveIntegerField()

    version = models.CharField(max_length=10)

    account_id = models.CharField(max_length=50)

    instance_id = models.CharField(max_length=50)

    srcaddr = models.GenericIPAddressField()

    dstaddr = models.GenericIPAddressField()

    srcport = models.PositiveIntegerField()

    dstport = models.PositiveIntegerField()

    protocol = models.PositiveIntegerField()

    packets = models.BigIntegerField()

    bytes = models.BigIntegerField()

    starttime = models.BigIntegerField(db_index=True)

    endtime = models.BigIntegerField(db_index=True)

    action = models.CharField(max_length=20)

    log_status = models.CharField(max_length=20)

    def __str__(self):
        return (
            f"{self.action} | "
            f"{self.srcaddr}:{self.srcport} -> "
            f"{self.dstaddr}:{self.dstport}"
        )
