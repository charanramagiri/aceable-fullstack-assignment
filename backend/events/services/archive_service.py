import tarfile
import tempfile
import time
from contextlib import ExitStack, contextmanager
from pathlib import Path


class InvalidArchiveError(Exception):
    """Raised when an uploaded archive cannot be safely processed."""


def is_event_archive(uploaded_file):
    file_name = uploaded_file.name.lower()

    return file_name.endswith(".tgz") or file_name.endswith(".tar.gz")


@contextmanager
def extract_event_archive(uploaded_file, metrics=None):
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_path = Path(temporary_directory)
        archive_path = temporary_path / "upload.tar.gz"
        extraction_path = temporary_path / "extracted"
        extraction_path.mkdir()

        copy_started = time.perf_counter()
        try:
            with archive_path.open("wb") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
        finally:
            if metrics is not None:
                metrics.archive_copy_seconds += time.perf_counter() - copy_started

        extraction_started = time.perf_counter()
        try:
            with tarfile.open(archive_path, "r:gz") as archive:
                members = archive.getmembers()

                for member in members:
                    member_path = (extraction_path / member.name).resolve()

                    if not member_path.is_relative_to(extraction_path.resolve()):
                        raise InvalidArchiveError("Invalid archive file.")

                    if not member.isfile() and not member.isdir():
                        raise InvalidArchiveError("Invalid archive file.")

                archive.extractall(extraction_path, members=members, filter="data")
        except (OSError, tarfile.TarError) as error:
            raise InvalidArchiveError("Invalid archive file.") from error
        finally:
            if metrics is not None:
                metrics.extraction_seconds += (
                    time.perf_counter() - extraction_started
                )

        extracted_files = [
            file_path
            for file_path in extraction_path.rglob("*")
            if file_path.is_file()
        ]

        if not extracted_files:
            raise InvalidArchiveError("Invalid archive file.")

        if metrics is not None:
            metrics.files += len(extracted_files)

        yield extracted_files


@contextmanager
def extract_event_archives(uploaded_files, metrics=None):
    with ExitStack() as stack:
        extracted_files = []

        for uploaded_file in uploaded_files:
            extracted_files.extend(
                stack.enter_context(extract_event_archive(uploaded_file, metrics))
            )

        yield extracted_files
