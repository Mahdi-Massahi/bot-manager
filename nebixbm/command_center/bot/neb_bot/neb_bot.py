import time

from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.command_center.tools.scheduler import Job, c2s, timestamp_now


class NebBot(BaseBot):
    """This is a template for bot class"""

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

        j = Job(self.test, timestamp_now() + c2s(seconds=5), ['aaa', 'bbbb'])
        while True:
            if j.can_run():
                j.run_now()
            time.sleep(1)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")

        # Do not delete this line:
        super().before_termination()

    def test(self, a, b):
        print(a, b)


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Neb Bot"
        version = "0.1.0"

        # Do not delete these lines:
        bot = NebBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
