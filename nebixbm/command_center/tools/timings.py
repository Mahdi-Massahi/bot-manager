import time
import datetime
from datetime import timezone


def timestamp_now(mili=True):
    """Return current timestamp"""
    return int(time.time() * 1000) if mili else time.time()


def datetime_to_timestamp(dt, is_utc=False, mili=True):
    """Converts datetime to timestamp"""
    if not is_utc:
        ts = dt.replace(tzinfo=timezone.utc).timestamp()
    else:
        ts = dt.timestamp()
    return int(ts * 1000) if mili else ts


def c2s(weeks=0, days=0, hours=0, minutes=0, seconds=0):
    """Converts to seconds"""
    return datetime.timedelta(
        weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds,
    ).total_seconds()
