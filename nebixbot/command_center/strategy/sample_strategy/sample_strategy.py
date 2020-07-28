from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class SampleStrategy(BaseStrategy):
    """This is a sample strategy"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        self.logger.info("inside before_start")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start")

    def before_termination(self):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("inside before_termination")

        # Do not delete this line:
        super().before_termination()

if __name__ == '__main__':
    try:
        # Change name and version of your strategy:
        name = 'sample strategy'
        version = '1.0.0'
        # Do not delete this line:
        strategy = SampleStrategy(name, version)
        strategy.logger.info("Successfully initialized strategy")
        # Do not delete this line:
        strategy.main()
    except Exception as err:
        if strategy is not None:
            strategy.logger.error(err)
