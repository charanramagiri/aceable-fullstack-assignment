from .services.parser_service import parse_all_uploaded_files

from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def parse_test(request):

    events = parse_all_uploaded_files()

    return Response({
        "total_events": len(events),
        "sample": events[:5]
    })
