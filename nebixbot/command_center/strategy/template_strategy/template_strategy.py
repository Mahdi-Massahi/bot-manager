#
# Import required modules here
#

from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class TemplateStrategy(BaseStrategy):
    """This is a template for strategy class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        #
        # Add your code here
        #

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        self.logger.info("inside before_start()")
        #
        # Add your code here
        #

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")
        #
        # Add your code here
        #

    def before_termination(self, *args, **kwargs):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("inside before_termination()")
        #
        # Add your code here
        #

        # Do not delete this line:
        super().before_termination()

    #
    # Add your functions here
    #


if __name__ == '__main__':
    try:

        # Change name and version of your strategy:
        name = 'Template Strategy'
        version = '1.0.0'

        # Do not delete these lines:
        strategy = TemplateStrategy(name, version)
        strategy.logger.info("Successfully initialized strategy")
        strategy.before_start()
        strategy.start()
    except Exception as err:
        if strategy is not None:
            strategy.logger.error(err)
            if not strategy.has_called_before_termination:
                strategy.before_termination()
