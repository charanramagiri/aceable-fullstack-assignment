from django.core.paginator import EmptyPage
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..services.search_service import search_events as search_event_records

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def get_pagination_params(data):
    try:
        page = int(data.get("page", DEFAULT_PAGE))
        page_size = int(data.get("page_size", DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        return None, "Page and page_size must be integers."

    if page < 1:
        return None, "Page must be greater than zero."

    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        return None, "Page size must be between 1 and 100."

    return (page, page_size), None


@api_view(["POST"])
def search_events(request):

    data = request.data
    pagination_params, error_message = get_pagination_params(data)

    if error_message:
        return Response(
            {"detail": error_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    page, page_size = pagination_params

    try:
        results = search_event_records(
            search_string=data.get("search"),
            earliest_time=data.get("earliest_time"),
            latest_time=data.get("latest_time"),
            page=page,
            page_size=page_size,
        )
    except EmptyPage:
        return Response(
            {"detail": "Page is out of range."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(results)
