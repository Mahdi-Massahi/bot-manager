from abc import ABC, abstractmethod
import sys
import signal

from nebixbot.log.logger import create_logger, get_file_name


class BaseStrategy(ABC):

    def __init__(self, name, version):
        """Initialize the class with given name and version"""
        self.name = name
        self.version = version
        filename = get_file_name(name, version)
        self.logger, self.log_filepath = create_logger(filename, filename)
        self.has_called_before_termination = False
        self.logger.info("Initialized strategy")

    def log_logfile_path(self):
        """Log logfile path into logger"""
        self.logger.info(f"Logger: {self.log_filepath}")

    def main(self):
        """Strategy entrypoint"""
        signal.signal(signal.SIGTERM, self.before_termination)
        try:
            self.before_start()
            self.start()
        except Exception as err:
            self.logger.error(err)
        finally:
            if not self.has_called_before_termination:
                self.before_termination()
            self.logger.info('Exiting now...')

    @abstractmethod
    def before_start(self):
        """Strategy Manager calls this method before running the strategy"""
        pass

    @abstractmethod
    def start(self):
        """Strategy Manager calls this method to run the strategy"""
        pass

    @abstractmethod
    def before_termination(self):
        """Strategy Manager calls this before terminating the running strategy
        """
        self.has_called_before_termination = True
        sys.exit()

    def __str__(self):
        """Strategy representation string"""
        return get_file_name(self.name, self.version)
