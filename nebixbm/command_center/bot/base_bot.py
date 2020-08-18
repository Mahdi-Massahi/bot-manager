from abc import ABC, abstractmethod
import sys
import signal

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
        """Bot Manager calls this before terminating the running bot
        """
        self.has_called_before_termination = True
        self.logger.info("Exiting now...")
        sys.exit()

    def __str__(self):
        """Bot representation string"""
        return get_file_name(self.name, self.version)
