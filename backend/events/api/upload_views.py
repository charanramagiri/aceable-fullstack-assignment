import logging
import time

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import FileUploadSerializer
from ..services.archive_service import (
    InvalidArchiveError,
    is_event_archive,
    extract_event_archives,
)
from ..services.archive_import_service import (
    EVENT_BATCH_SIZE,
    UPLOADED_FILE_BATCH_SIZE,
    import_archive_events,
)
from ..services.archive_benchmark import (
    ArchiveImportMetrics,
    BENCHMARK_LOGGER_NAME,
)
from ..services.parser_service import InvalidEventFileError

benchmark_logger = logging.getLogger(BENCHMARK_LOGGER_NAME)


@api_view(["POST"])
def upload_files(request):
    request_started = time.perf_counter()
    metrics = ArchiveImportMetrics(
        uploaded_file_batch_size=UPLOADED_FILE_BATCH_SIZE,
        event_batch_size=EVENT_BATCH_SIZE,
    )

    try:
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            files = serializer.validated_data["files"]
            metrics.archives = len(files)

            if not all(is_event_archive(file) for file in files):
                metrics.error_stage = "archive_validation"
                return Response(
                    {"detail": "Only .tgz and .tar.gz uploads are supported."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                metrics.error_stage = "extraction"
                with extract_event_archives(files, metrics) as extracted_files:
                    metrics.error_stage = "import"
                    response_files = import_archive_events(extracted_files, metrics)
            except (InvalidArchiveError, InvalidEventFileError) as error:
                return Response(
                    {"detail": str(error)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            metrics.outcome = "success"
            metrics.error_stage = "none"
            return Response(
                {
                    "status": "success",
                    "message": f"{len(response_files)} file(s) uploaded successfully.",
                    "files": response_files,
                },
                status=status.HTTP_201_CREATED,
            )

        metrics.error_stage = "request_validation"
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    finally:
        metrics.request_seconds = time.perf_counter() - request_started
        benchmark_logger.info(metrics.summary())
