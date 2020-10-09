from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.database.driver import RedisDB


# Change name and version of your bot:
name = "Redis Bot"
version = "1.0.0"


class RedisBot(BaseBot):
    """Redis bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        #
        # Add your code here
        #

    def before_start(self):
        """Bot Manager calls this before running the bot"""
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
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        res = self.redis.delete(self.key)
        if res:
            self.logger.info(f"successfully deleted key: {self.key}")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:
        # Do not delete these lines:
        bot = RedisBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
        bot.before_termination()
    except Exception as err:
        if bot is not None:
            bot.logger.exception(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
