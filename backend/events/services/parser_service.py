from pathlib import Path


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

INTEGER_FIELDS = [
    "serialno",
    "srcport",
    "dstport",
    "protocol",
    "packets",
    "bytes",
    "starttime",
    "endtime",
]


class InvalidEventFileError(Exception):
    """Raised when an event file contains invalid data."""


def parse_event_line(line):
    parts = line.strip().split()

    if len(parts) != len(EVENT_FIELDS):
        return None

    return dict(zip(EVENT_FIELDS, parts))


def parse_event_file(file_path):
    file_path = Path(file_path)
    event_count = 0

    try:
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                event = parse_event_line(line)

                if event is None:
                    raise InvalidEventFileError("Invalid event file format.")

                try:
                    for field in INTEGER_FIELDS:
                        int(event[field])
                except ValueError as error:
                    raise InvalidEventFileError("Invalid event file format.") from error

                event_count += 1
                yield event
    except (OSError, UnicodeDecodeError) as error:
        raise InvalidEventFileError("Invalid event file format.") from error

    if event_count == 0:
        raise InvalidEventFileError("Invalid event file format.")
