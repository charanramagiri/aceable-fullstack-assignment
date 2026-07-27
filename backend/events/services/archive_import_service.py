from django.db import transaction

from events.models import Event, UploadedFile

from .parser_service import parse_event_file

UPLOADED_FILE_BATCH_SIZE = 500
EVENT_BATCH_SIZE = 1000


def import_archive_events(file_paths):
    with transaction.atomic():
        parsed_files = []

        for file_path in file_paths:
            events = list(parse_event_file(file_path))
            parsed_files.append((file_path, events))

        uploaded_files = [
            UploadedFile(
                filename=file_path.name,
                event_count=len(events),
            )
            for file_path, events in parsed_files
        ]
        uploaded_files = UploadedFile.objects.bulk_create(
            uploaded_files,
            batch_size=UPLOADED_FILE_BATCH_SIZE,
        )

        event_objects = []

        for uploaded_file, (_, events) in zip(uploaded_files, parsed_files):
            event_objects.extend(
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
                for event in events
            )

        Event.objects.bulk_create(event_objects, batch_size=EVENT_BATCH_SIZE)

    return [uploaded_file.filename for uploaded_file in uploaded_files]
