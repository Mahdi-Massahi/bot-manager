from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class SampleStrategy(BaseStrategy):
    """This is a sample strategy"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        pass
        # self.logger.error("it's before start")

    def start(self):
        """This method is called when algorithm is run"""
        pass
        # self.logger.error("it's start")

    def before_termination(self):
        """Strategy Manager calls this before terminating a running strategy"""
        pass
        # self.logger.error("it's before termination")

if __name__ == '__main__':
    strategy = SampleStrategy('sample strategy', '1.0')
    strategy.before_start()
    strategy.start()
    strategy.before_termination()
