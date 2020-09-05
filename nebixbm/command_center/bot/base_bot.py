from abc import ABC, abstractmethod
import sys
import signal
import os
import psutil
import time

from nebixbm.log.logger import create_logger, get_file_name


class BaseBot(ABC):
    def __init__(self, name, version):
        """Initialize the class with given name and version"""
        self.name = name
        self.version = version
        filename = get_file_name(name, version)
        self.logger, self.log_filepath = create_logger(filename, filename)
        self.has_called_before_termination = False
        self.logger.info("Initialized bot")
        signal.signal(signal.SIGTERM, self.before_termination)

    def log_logfile_path(self):
        """Log logfile path into logger"""
        self.logger.info(f"Logger: {self.log_filepath}")

    @abstractmethod
    def before_start(self):
        """Bot Manager calls this method before running the bot"""
        pass

    @abstractmethod
    def start(self):
        """Bot Manager calls this method to run the bot"""
        pass

    @abstractmethod
    def before_termination(self):
        """Bot Manager calls this before terminating the running bot"""
        self.has_called_before_termination = True
        self.logger.info("Exiting now...")
        sys.exit()

    def _terminate_subprocess(self, pid, clean_up_time) -> bool:
        """"Terminates(stops) given pid"""
        if not psutil.pid_exists(pid):
            self.logger.error("pid does NOT exist in the system")
            return False

        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            self.logger.info(f"Sent SIGTERM to pid={pid}")
            self.logger.info(
                f"Waiting {clean_up_time} seconds"
                + " to let the subprocess clean up"
            )
            time.sleep(clean_up_time)

            if psutil.pid_exists(pid):
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                self.logger.info(
                    "Subprocess was not terminated, "
                    + f"sent another SIGTERM to pid={pid}"
                )

            else:
                self.logger.info(
                    "Successfully terminated " + f"subprocess (pid={pid})"
                )
                return True
        except Exception as err:
            self.logger.error(err)
            return False

    def run_with_timeout(
        self,
        func,
        params,
        timeout_duration: float,
        return_on_timeout
    ):
        """Runs a function with given parameters and returns the function's
        return value. If timeout duration passed it terminates the function
        and returns the default return value.
        """

        class TimeoutError(Exception):
            pass

        def handler(signum, frame):
            raise TimeoutError()

        signal.signal(signal.SIGALRM, handler)
        signal.setitimer(signal.ITIMER_REAL, timeout_duration)
        try:
            result = func(params)
        except TimeoutError:
            result = return_on_timeout
        finally:
            signal.alarm(0)

        return result

    def __str__(self):
        """Bot representation string"""
        return get_file_name(self.name, self.version)
