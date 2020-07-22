from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class SampleStrategy(BaseStrategy):
    """This is a sample strategy"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        self.logger.error("it's before start")
        return "before start"

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.error("it's start")
        return "start"

    def before_termination(self):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.error("it's before termination")
        return "before termination"
