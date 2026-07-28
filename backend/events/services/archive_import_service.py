import time

from django.db import transaction

from events.models import Event, UploadedFile

from .archive_service import InvalidArchiveError
from .parser_service import parse_event_stream

UPLOADED_FILE_BATCH_SIZE = 500
EVENT_BATCH_SIZE = 1000


class DuplicateArchiveMemberError(Exception):
    """Raised when an exact archive-member basename has already been submitted."""

    def __init__(self, filename, *, already_imported):
        self.filename = filename
        self.already_imported = already_imported
        super().__init__(filename)


def import_archive_events(archive_members, metrics=None):
    import_started = time.perf_counter()
    try:
        with transaction.atomic():
            if metrics is not None:
                metrics.error_stage = "duplicate_detection"
            duplicate_check_started = time.perf_counter()
            try:
                existing_filenames = set(
                    UploadedFile.objects.values_list("filename", flat=True)
                )
            finally:
                if metrics is not None:
                    metrics.duplicate_check_seconds += (
                        time.perf_counter() - duplicate_check_started
                    )

            if metrics is not None:
                metrics.duplicate_existing_filename_count = len(
                    existing_filenames
                )

            submitted_filenames = set()
            parsed_files = []

            for archive_member in archive_members:
                if metrics is not None:
                    metrics.error_stage = "duplicate_detection"
                duplicate_check_started = time.perf_counter()
                try:
                    # This experiment intentionally treats exact, case-sensitive
                    # basename matches as duplicates regardless of file contents.
                    if archive_member.filename in existing_filenames:
                        raise DuplicateArchiveMemberError(
                            archive_member.filename,
                            already_imported=True,
                        )
                    if archive_member.filename in submitted_filenames:
                        raise DuplicateArchiveMemberError(
                            archive_member.filename,
                            already_imported=False,
                        )
                    submitted_filenames.add(archive_member.filename)
                finally:
                    if metrics is not None:
                        metrics.duplicate_check_seconds += (
                            time.perf_counter() - duplicate_check_started
                        )

                if metrics is not None:
                    metrics.error_stage = "parsing"
                parsing_started = time.perf_counter()
                try:
                    events = list(parse_event_stream(archive_member.stream))
                except InvalidArchiveError:
                    if metrics is not None:
                        metrics.error_stage = "archive_streaming"
                    raise
                finally:
                    if metrics is not None:
                        metrics.parsing_seconds += (
                            time.perf_counter() - parsing_started
                        )
                parsed_files.append((archive_member.filename, events))

            uploaded_files = [
                UploadedFile(
                    filename=filename,
                    event_count=len(events),
                )
                for filename, events in parsed_files
            ]
            if metrics is not None:
                metrics.error_stage = "uploaded_file_insert"
            uploaded_file_insert_started = time.perf_counter()
            try:
                uploaded_files = UploadedFile.objects.bulk_create(
                    uploaded_files,
                    batch_size=UPLOADED_FILE_BATCH_SIZE,
                )
            finally:
                if metrics is not None:
                    metrics.uploaded_file_insert_seconds += (
                        time.perf_counter() - uploaded_file_insert_started
                    )

            event_objects = []

            if metrics is not None:
                metrics.error_stage = "event_object_creation"
            event_object_creation_started = time.perf_counter()
            try:
                for uploaded_file, (_, events) in zip(uploaded_files, parsed_files):
                    event_objects.extend(
                        Event(
                            uploaded_file=uploaded_file,
                            serialno=event.serialno,
                            version=event.version,
                            account_id=event.account_id,
                            instance_id=event.instance_id,
                            srcaddr=event.srcaddr,
                            dstaddr=event.dstaddr,
                            srcport=event.srcport,
                            dstport=event.dstport,
                            protocol=event.protocol,
                            packets=event.packets,
                            bytes=event.bytes,
                            starttime=event.starttime,
                            endtime=event.endtime,
                            action=event.action,
                            log_status=event.log_status,
                        )
                        for event in events
                    )
            finally:
                if metrics is not None:
                    metrics.event_object_creation_seconds += (
                        time.perf_counter() - event_object_creation_started
                    )

            if metrics is not None:
                metrics.error_stage = "event_insert"
            event_insert_started = time.perf_counter()
            try:
                Event.objects.bulk_create(
                    event_objects,
                    batch_size=EVENT_BATCH_SIZE,
                )
            finally:
                if metrics is not None:
                    metrics.event_insert_seconds += (
                        time.perf_counter() - event_insert_started
                    )

        if metrics is not None:
            metrics.events = len(event_objects)
        return [uploaded_file.filename for uploaded_file in uploaded_files]
    finally:
        if metrics is not None:
            metrics.import_seconds += time.perf_counter() - import_started
