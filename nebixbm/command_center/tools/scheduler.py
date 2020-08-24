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
                weeks=weeks,
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            ).total_seconds()


class Job:
    """Job, to run a function with given args at a specified timestamp"""

    def __init__(self, function, ts, args: list):
        """Initialize Job
        Warning: timestamp should be in miliseconds!
        """
        self._function = function
        self._timestamp = ts
        self._args = args
        self.has_run = False

    @property
    def function(self):
        """Getter for job's function"""
        return self._function

    @function.setter
    def function(self, value):
        """Setter for job's function"""
        self._function = value

    @property
    def timestamp(self):
        """Getter for job's timestamp"""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        """Setter for job's timestamp
        Warning: timestamp should be in miliseconds!
        """
        self._timestamp = value

    @property
    def args(self):
        """Getter for job's args"""
        return self._args

    @args.setter
    def args(self, value: list):
        """Setter for job's args"""
        self._args = value

    def run_now(self):
        """Runs job's function immediately"""
        self.has_run = True
        return self._function(*self._args)

    def can_run(self):
        """Checks whether it has reached the timestamp"""
        time_now = int(time.time() * 1000)  # convert to miliseconds
        return time_now >= self.timestamp
