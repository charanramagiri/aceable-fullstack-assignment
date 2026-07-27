from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import FileUploadSerializer
from ..services.archive_service import (
    InvalidArchiveError,
    is_event_archive,
    extract_event_archives,
)
from ..services.archive_import_service import import_archive_events
from ..services.parser_service import InvalidEventFileError


@api_view(["POST"])
def upload_files(request):
    serializer = FileUploadSerializer(data=request.data)

    if serializer.is_valid():
        files = serializer.validated_data["files"]

        if not all(is_event_archive(file) for file in files):
            return Response(
                {"detail": "Only .tgz and .tar.gz uploads are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with extract_event_archives(files) as extracted_files:
                response_files = import_archive_events(extracted_files)
        except (InvalidArchiveError, InvalidEventFileError) as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status": "success",
                "message": f"{len(response_files)} file(s) uploaded successfully.",
                "files": response_files,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
