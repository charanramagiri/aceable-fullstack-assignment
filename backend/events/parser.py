EVENT_FIELDS = [
    "serialno",
    "version",
    "account_id",
    "instance_id",
    "srcaddr",
    "dstaddr",
    "srcport",
    "dstport",
    "protocol",
    "packets",
    "bytes",
    "starttime",
    "endtime",
    "action",
    "log_status",
]

def parse_event_line(line):
    """
    Parse a single event line into a dictionary.
    Returns None if the line is invalid.
    """

    line = line.strip()

    if not line:
        return None

    parts = line.split()

    if len(parts) != len(EVENT_FIELDS):
        return None

    event = dict(zip(EVENT_FIELDS, parts))

    return event

from pathlib import Path


def parse_event_file(file_path):
    """
    Parse one event file.
    Returns a list of event dictionaries.
    """

    events = []

    file_path = Path(file_path)

    with open(file_path, "r") as file:

        for line in file:

            event = parse_event_line(line)

            if event:

                event["file_name"] = file_path.name

                events.append(event)

    return events

from django.conf import settings


def parse_all_uploaded_files():
    """
    Parse every uploaded event file.
    Returns one combined list of all events.
    """

    all_events = []

    upload_dir = Path(settings.MEDIA_ROOT)

    if not upload_dir.exists():
        return all_events

    for file_path in upload_dir.iterdir():

        if file_path.is_file():

            events = parse_event_file(file_path)

            all_events.extend(events)

    return all_events