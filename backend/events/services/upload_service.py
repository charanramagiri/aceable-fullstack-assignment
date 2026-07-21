import os
from django.conf import settings
from pathlib import Path
from events.models import UploadedFile
from events.models import Event


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


from .parser_service import parse_event_file


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
                srcaddr=event["srcaddr"],
                dstaddr=event["dstaddr"],
                action=event["action"],
                starttime=event["starttime"],
                log_status=event["log_status"],
            )
        )

    Event.objects.bulk_create(event_objects)