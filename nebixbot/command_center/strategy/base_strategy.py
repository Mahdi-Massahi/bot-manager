from abc import ABC, abstractmethod

from nebixbot.log.logger import create_logger


class BaseStrategy(ABC):


    def __init__(self, name, version):
        """Initialize the class with given name and version"""
        self.name = name
        self.version = version
        self.logger = create_logger(f'{name}_{version}', f'{name}_{version}')

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
        return self.name
