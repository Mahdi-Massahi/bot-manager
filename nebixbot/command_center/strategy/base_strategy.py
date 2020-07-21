from abc import ABC, abstractmethod


class BaseStrategy(ABC):

    @abstractmethod
    def __init__(self, name, version):
        """Initialize the class with given name and version"""
        pass

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
