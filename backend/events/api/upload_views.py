from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import FileUploadSerializer
from ..services.upload_service import save_uploaded_files
from ..services.cache_service import refresh_cache


@api_view(["POST"])
def upload_files(request):
    serializer = FileUploadSerializer(data=request.data)

    if serializer.is_valid():
        files = serializer.validated_data["files"]

        saved_files = save_uploaded_files(files)

        # Refresh the in-memory cache after uploading new files
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