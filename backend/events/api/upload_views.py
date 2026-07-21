from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import FileUploadSerializer
from ..services.parser_service import validate_uploaded_event_file
from ..services.upload_service import save_uploaded_files
from ..services.cache_service import refresh_cache
from ..services.upload_service import store_events_in_database


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

        saved_files = save_uploaded_files(files)

        for file_path in saved_files:
            store_events_in_database(file_path)

        refresh_cache()

        return Response(
            {
                "status": "success",
                "message": f"{len(saved_files)} file(s) uploaded successfully.",
                "files": saved_files,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
