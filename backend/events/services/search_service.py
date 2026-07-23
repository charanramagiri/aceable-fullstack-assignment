import time

from django.db.models import Q
from django.core.paginator import Paginator

from events.models import Event


def search_events(
    search_string=None,
    earliest_time=None,
    latest_time=None,
    page=1,
    page_size=20,
):
    """
    Search events stored in SQLite.
    """

    start = time.perf_counter()

    queryset = Event.objects.select_related("uploaded_file").order_by("id")

    # Search text
    if search_string:
        queryset = queryset.filter(
            Q(account_id__icontains=search_string)
            | Q(instance_id__icontains=search_string)
            | Q(srcaddr__icontains=search_string)
            | Q(dstaddr__icontains=search_string)
            | Q(action__icontains=search_string)
            | Q(log_status__icontains=search_string)
        )

    # Earliest time filter
    if earliest_time:
        queryset = queryset.filter(
            starttime__gte=int(earliest_time)
        )

    # Latest time filter
    if latest_time:
        queryset = queryset.filter(
            endtime__lte=int(latest_time)
        )

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.page(page)

    results = []

    for event in page_obj:

        results.append(
            {
                "serialno": event.serialno,
                "version": event.version,
                "account_id": event.account_id,
                "instance_id": event.instance_id,
                "srcaddr": event.srcaddr,
                "dstaddr": event.dstaddr,
                "srcport": event.srcport,
                "dstport": event.dstport,
                "protocol": event.protocol,
                "packets": event.packets,
                "bytes": event.bytes,
                "starttime": event.starttime,
                "endtime": event.endtime,
                "action": event.action,
                "log_status": event.log_status,
                "file_name": event.uploaded_file.filename,
            }
        )

    elapsed = round(time.perf_counter() - start, 4)

    return {
        "count": paginator.count,
        "page": page_obj.number,
        "page_size": page_size,
        "total_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "search_time": elapsed,
        "results": results,
    }
