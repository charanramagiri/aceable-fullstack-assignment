from .parser import parse_all_uploaded_files

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import FileUploadSerializer
from .utils import save_uploaded_files

from .search_engine import search_events

@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "success",
        "message": "Aceable Backend is running."
    })


@api_view(["POST"])
def upload_files(request):
    serializer = FileUploadSerializer(data=request.data)

    if serializer.is_valid():
        files = serializer.validated_data["files"]

        saved_files = save_uploaded_files(files)

        return Response(
            {
                "status": "success",
                "message": f"{len(saved_files)} file(s) uploaded successfully.",
                "files": saved_files,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def parse_test(request):

    events = parse_all_uploaded_files()

    return Response({
        "total_events": len(events),
        "sample": events[:5]
    })

@api_view(["POST"])
def search_test(request):

    data = request.data

    results = search_events(
        search_string=data.get("search"),
        earliest_time=data.get("earliest_time"),
        latest_time=data.get("latest_time"),
    )

    return Response(results)