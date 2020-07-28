import time


from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class SampleStrategy2(BaseStrategy):
    """This is a sample strategy"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        self.logger.info("BEFORE START")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("START")
        time.sleep(100)

    def before_termination(self, *args, **kwargs):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("BEFORE TERMINATION")
        time.sleep(5)

        # Do not delete this line:
        super().before_termination()


if __name__ == '__main__':
    strategy = SampleStrategy2('Sample Strategy 2', '0.0.1')
    strategy.main()
