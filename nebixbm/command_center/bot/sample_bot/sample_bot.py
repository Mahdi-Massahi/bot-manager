from nebixbm.command_center.bot.base_bot import BaseBot


class SampleBot(BaseBot):
    """This is a sample bot"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start")

    def before_termination(self):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:
        # Change name and version of your bot:
        name = "sample bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = SampleBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
        bot.before_termination()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
