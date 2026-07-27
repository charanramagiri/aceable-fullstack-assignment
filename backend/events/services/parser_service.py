import gzip
import io
import tarfile
import zlib
from pathlib import Path
from typing import NamedTuple

from .archive_service import InvalidArchiveError


class ParsedEvent(NamedTuple):
    serialno: int
    version: str
    account_id: str
    instance_id: str
    srcaddr: str
    dstaddr: str
    srcport: int
    dstport: int
    protocol: int
    packets: int
    bytes: int
    starttime: int
    endtime: int
    action: str
    log_status: str


class InvalidEventFileError(Exception):
    """Raised when an event file contains invalid data."""


def parse_event_line(line):
    parts = line.strip().split()

    if len(parts) != len(ParsedEvent._fields):
        return None

    try:
        return ParsedEvent(
            serialno=int(parts[0]),
            version=parts[1],
            account_id=parts[2],
            instance_id=parts[3],
            srcaddr=parts[4],
            dstaddr=parts[5],
            srcport=int(parts[6]),
            dstport=int(parts[7]),
            protocol=int(parts[8]),
            packets=int(parts[9]),
            bytes=int(parts[10]),
            starttime=int(parts[11]),
            endtime=int(parts[12]),
            action=parts[13],
            log_status=parts[14],
        )
    except ValueError as error:
        raise InvalidEventFileError("Invalid event file format.") from error


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

                event_count += 1
                yield event
    except (OSError, UnicodeDecodeError) as error:
        raise InvalidEventFileError("Invalid event file format.") from error

    if event_count == 0:
        raise InvalidEventFileError("Invalid event file format.")


def parse_event_stream(binary_stream):
    text_stream = io.TextIOWrapper(binary_stream, encoding="utf-8")
    event_count = 0

    try:
        for line in text_stream:
            if not line.strip():
                continue

            event = parse_event_line(line)

            if event is None:
                raise InvalidEventFileError("Invalid event file format.")

            event_count += 1
            yield event
    except (EOFError, gzip.BadGzipFile, tarfile.TarError, zlib.error) as error:
        raise InvalidArchiveError("Invalid archive file.") from error
    except (OSError, UnicodeDecodeError) as error:
        raise InvalidEventFileError("Invalid event file format.") from error
    finally:
        text_stream.detach()

    if event_count == 0:
        raise InvalidEventFileError("Invalid event file format.")
