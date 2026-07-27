import tarfile
import time
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import BinaryIO, Iterator


class InvalidArchiveError(Exception):
    """Raised when an uploaded archive cannot be safely processed."""


@dataclass
class EventArchiveMember:
    filename: str
    stream: BinaryIO


def is_event_archive(uploaded_file):
    file_name = uploaded_file.name.lower()

    return file_name.endswith(".tgz") or file_name.endswith(".tar.gz")


def iter_event_archive_members(
    uploaded_files,
    metrics=None,
) -> Iterator[EventArchiveMember]:
    for uploaded_file in uploaded_files:
        archive = None
        regular_file_count = 0
        try:
            if metrics is not None:
                metrics.error_stage = "archive_streaming"
            inspection_started = time.perf_counter()
            try:
                uploaded_file.seek(0)
                archive = tarfile.open(fileobj=uploaded_file, mode="r:gz")
            finally:
                if metrics is not None:
                    metrics.archive_streaming_seconds += (
                        time.perf_counter() - inspection_started
                    )

            member_iterator = iter(archive)
            while True:
                if metrics is not None:
                    metrics.error_stage = "archive_streaming"
                inspection_started = time.perf_counter()
                try:
                    member = next(member_iterator)
                except StopIteration:
                    break
                finally:
                    if metrics is not None:
                        metrics.archive_streaming_seconds += (
                            time.perf_counter() - inspection_started
                        )

                if member.isdir():
                    continue

                if not member.isfile():
                    raise InvalidArchiveError("Invalid archive file.")

                if metrics is not None:
                    metrics.error_stage = "archive_streaming"
                inspection_started = time.perf_counter()
                try:
                    member_stream = archive.extractfile(member)
                finally:
                    if metrics is not None:
                        metrics.archive_streaming_seconds += (
                            time.perf_counter() - inspection_started
                        )

                if member_stream is None:
                    raise InvalidArchiveError("Invalid archive file.")

                regular_file_count += 1
                if metrics is not None:
                    metrics.files += 1

                try:
                    yield EventArchiveMember(
                        filename=PurePosixPath(member.name).name,
                        stream=member_stream,
                    )
                finally:
                    member_stream.close()

            if regular_file_count == 0:
                raise InvalidArchiveError("Invalid archive file.")
        except InvalidArchiveError:
            raise
        except (EOFError, OSError, tarfile.TarError) as error:
            raise InvalidArchiveError("Invalid archive file.") from error
        finally:
            if archive is not None:
                archive.close()
