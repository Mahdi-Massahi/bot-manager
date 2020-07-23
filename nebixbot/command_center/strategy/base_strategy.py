from abc import ABC, abstractmethod

from nebixbot.log.logger import create_logger, get_file_name


class BaseStrategy(ABC):

    def __init__(self, name, version):
        """Initialize the class with given name and version"""
        self.name = name
        self.version = version
        filename = get_file_name(name, version)
        self.logger = create_logger(filename, filename)

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
        pass

    def __str__(self):
        """Strategy representation string"""
        return get_file_name(self.name, self.version)
