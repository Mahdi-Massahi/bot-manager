import time

from nebixbm.command_center.bot.base_bot import BaseBot


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
        self.logger.info("inside start()")
        while True:
            to = random.uniform(0.5, 1.5)
            result = self.run_with_timeout(self.func, "params", to, False)
            self.logger.info(f"result: {result}")

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        # Do not delete this line:
        super().before_termination()

    def func(self, param):
        """Some random func"""
        self.logger.info("func beginning")
        time.sleep(1)
        self.logger.info("func end")
        return True


if __name__ == "__main__":
    try:
        name = "Timeout Bot"
        version = "1.0.0"

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
