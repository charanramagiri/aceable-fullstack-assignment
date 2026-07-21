import os
from django.conf import settings
from pathlib import Path
from events.models import UploadedFile
from events.models import Event
from .parser_service import parse_event_file


def save_uploaded_files(files):
    """
    Save uploaded files to MEDIA_ROOT.
    Returns a list of saved filenames.
    """

    saved_files = []

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    for file in files:
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        saved_files.append(file_path)

    return saved_files


def find_duplicate_filenames(files):
    """
    Returns a list of filenames that have already been uploaded.
    """

    duplicates = []

    for file in files:
        if UploadedFile.objects.filter(filename=file.name).exists():
            duplicates.append(file.name)

    return duplicates




def store_events_in_database(file_path):
    """
    Parse one uploaded file and store its events in SQLite.
    """

    file_path = Path(file_path)

    parsed_events = parse_event_file(file_path)

    uploaded_file = UploadedFile.objects.create(
        filename=file_path.name,
        event_count=len(parsed_events),
    )

    event_objects = []

    for event in parsed_events:

        event_objects.append(
            Event(
                uploaded_file=uploaded_file,

                serialno=int(event["serialno"]),
                version=event["version"],

                account_id=event["account_id"],
                instance_id=event["instance_id"],

                srcaddr=event["srcaddr"],
                dstaddr=event["dstaddr"],

                srcport=int(event["srcport"]),
                dstport=int(event["dstport"]),

                protocol=int(event["protocol"]),

                packets=int(event["packets"]),
                bytes=int(event["bytes"]),

                starttime=int(event["starttime"]),
                endtime=int(event["endtime"]),

                action=event["action"],
                log_status=event["log_status"],
            )
        )

    Event.objects.bulk_create(event_objects)