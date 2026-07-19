import time

from .parser_service import parse_all_uploaded_files

SEARCH_FIELDS = [
    "account_id",
    "instance_id",
    "srcaddr",
    "dstaddr",
    "action",
    "log_status",
]

def matches_search_string(event, search_string):
    """
    Returns True if search_string matches
    any searchable field.
    """

    if not search_string:
        return True

    search_string = search_string.strip().lower()

    for field in SEARCH_FIELDS:

        value = str(event.get(field, "")).lower()

        if search_string in value:
            return True

    return False

def matches_time_range(event, earliest_time=None, latest_time=None):
    """
    Check whether the event falls
    within the requested time range.
    """

    start = int(event["starttime"])
    end = int(event["endtime"])

    if earliest_time:

        if start < int(earliest_time):
            return False

    if latest_time:

        if end > int(latest_time):
            return False

    return True

def search_events(
    search_string=None,
    earliest_time=None,
    latest_time=None,
):
    """
    Search uploaded event files.
    """

    start_time = time.perf_counter()

    events = parse_all_uploaded_files()

    results = []

    for event in events:

        if not matches_search_string(event, search_string):
            continue

        if not matches_time_range(
            event,
            earliest_time,
            latest_time,
        ):
            continue

        results.append(event)

    elapsed = round(time.perf_counter() - start_time, 4)

    return {
        "count": len(results),
        "search_time": elapsed,
        "results": results,
    }