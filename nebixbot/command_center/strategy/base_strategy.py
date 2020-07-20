from abc import ABC, abstractmethod


class BaseStrategy(ABC):

    def __init__(self, name, version):
        self.name = name
        self.version = version

    @abstractmethod
    def before_start():
        pass

    @abstractmethod
    def start():
        pass

    @abstractmethod
    def before_termination():
        pass
