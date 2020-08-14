from nebixbot.command_center.strategy.base_strategy import BaseStrategy
from nebixbot.database.driver import RedisDB


class RedisStrategy(BaseStrategy):
    """Redis strategy class"""

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
        self.redis = RedisDB()
        self.key = "before_start_variable"
        self.value = "check"
        self.redis.set(self.key, self.value)

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")
        res = self.redis.get(self.key)
        if res and res == self.value:
            self.logger.info(f"{self.key} exists and the value was: {res}")

    def before_termination(self, *args, **kwargs):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("inside before_termination()")
        res = self.redis.delete(self.key)
        if res:
            self.logger.info(f"successfully deleted key: {self.key}")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:

        # Change name and version of your strategy:
        name = "Redis Strategy"
        version = "1.0.0"

        # Do not delete these lines:
        strategy = RedisStrategy(name, version)
        strategy.logger.info("Successfully initialized strategy")
        strategy.before_start()
        strategy.start()
        strategy.before_termination()
    except Exception as err:
        if strategy is not None:
            strategy.logger.exception(err)
            if not strategy.has_called_before_termination:
                strategy.before_termination()
