import time


from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class SampleStrategy2(BaseStrategy):
    """This is a sample strategy"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)
        self.x = 0

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        self.logger.info("BEFORE START")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("START")
        while True:
            if self.x > 100:
                break
            self.x += 1
            self.logger.info(self.x)
            time.sleep(1)

    def before_termination(self, *args, **kwargs):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("BEFORE TERMINATION")
        time.sleep(10)
        self.logger.info(f"final number: {self.x}")

        # Do not delete this line:
        super().before_termination()


if __name__ == '__main__':
    try:

        # Change name and version of your strategy:
        name = 'sample strategy 2'
        version = '1.0.0'

        # Do not delete these lines:
        strategy = SampleStrategy2(name, version)
        strategy.logger.info("Successfully initialized strategy")
        strategy.before_start()
        strategy.start()
    except Exception as err:
        if strategy is not None:
            strategy.logger.error(err)
            if not strategy.has_called_before_termination:
                strategy.before_termination()
