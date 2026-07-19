from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..services.search_service import search_events


@api_view(["POST"])
def search_test(request):

    data = request.data

    results = search_events(
        search_string=data.get("search"),
        earliest_time=data.get("earliest_time"),
        latest_time=data.get("latest_time"),
    )

    return Response(results)