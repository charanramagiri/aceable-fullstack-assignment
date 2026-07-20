from .parser_service import parse_all_uploaded_files

# In-memory cache
EVENT_CACHE = []


def load_cache():
    """
    Load all parsed events into memory.
    """
    global EVENT_CACHE
    EVENT_CACHE = parse_all_uploaded_files()


def refresh_cache():
    """
    Refresh cache after new uploads.
    """
    load_cache()


def get_cache():
    """
    Return cached events.
    """
    return EVENT_CACHE


def clear_cache():
    """
    Clear the cache.
    """
    global EVENT_CACHE
    EVENT_CACHE = []