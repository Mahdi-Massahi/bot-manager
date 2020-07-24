import sys
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
        time.sleep(30)

    def before_termination(self):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("BEFORE TERMINATION")


if __name__ == '__main__':
    strategy = SampleStrategy2('Sample Strategy 2', '0.0.1')
    try:
        strategy.before_start()
        strategy.start()
        strategy.before_termination()
    except Exception as err:
        strategy.logger.error(err)
    finally:
        strategy.logger.info('Exiting Now...')
        sys.exit()
