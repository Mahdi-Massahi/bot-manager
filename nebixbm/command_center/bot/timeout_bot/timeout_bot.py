import time

from nebixbm.command_center.bot.base_bot import BaseBot


name = "Timeout Bot"
version = "1.0.0"


class TimeoutBot(BaseBot):
    """Timeout bot to test timeout of function(s)"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.debug("inside start()")
        while True:
            result = self.run_with_timeout(self.func, "params", 10, False)
            if result:
                self.logger.error(f"result: {result}")
            else:
                self.logger.info(f"result: {result}")

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        # Do not delete this line:
        super().before_termination()

    def func(self, param):
        """Some random func"""
        self.logger.info("func beginning")
        res2 = self.run_with_timeout(self.func2, param, 3, False)
        time.sleep(3)
        if res2:
            self.logger.info("func2 did a good job")
        else:
            self.logger.info("func2 screwed up")
        time.sleep(3)
        self.logger.info("func end")
        return True

    def func2(self, param):
        """Some random func"""
        self.logger.info("func2 beginning")
        time.sleep(10000)
        self.logger.info("func2 end")
        return True


if __name__ == "__main__":
    try:
        # Do not delete these lines:
        bot = TimeoutBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
