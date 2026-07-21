from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import FileUploadSerializer
from ..services.parser_service import validate_uploaded_event_file
from ..services.upload_service import (
    save_uploaded_files,
    store_events_in_database,
    find_duplicate_filenames,
)


@api_view(["POST"])
def upload_files(request):
    serializer = FileUploadSerializer(data=request.data)

    if serializer.is_valid():
        files = serializer.validated_data["files"]

        if not all(validate_uploaded_event_file(file) for file in files):
            return Response(
                {"detail": "Invalid event file format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for duplicate filenames before saving any files
        duplicates = find_duplicate_filenames(files)

        if duplicates:
            return Response(
                {
                    "status": "error",
                    "message": "One or more files have already been uploaded.",
                    "duplicates": duplicates,
                },
                status=status.HTTP_409_CONFLICT,
            )

        saved_files = save_uploaded_files(files)

        for file_path in saved_files:
            store_events_in_database(file_path)

        return Response(
            {
                "status": "success",
                "message": f"{len(saved_files)} file(s) uploaded successfully.",
                "files": saved_files,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)