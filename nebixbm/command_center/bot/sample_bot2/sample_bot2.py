import time


from nebixbm.command_center.bot.base_bot import BaseBot


# Change name and version of your bot:
name = "sample bot 2"
version = "1.0.0"


class SampleBot2(BaseBot):
    """This is a sample bot"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)
        self.x = 0

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("BEFORE START")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("START")
        while True:
            if self.x > 1000:
                break
            self.x += 1
            self.logger.info(self.x)
            time.sleep(1)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("BEFORE TERMINATION")
        time.sleep(10)
        self.logger.info(f"final number: {self.x}")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:
        # Do not delete these lines:
        bot = SampleBot2(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
