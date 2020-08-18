#
# Import required modules here
#

from nebixbm.command_center.bot.base_bot import BaseBot


class TemplateBot(BaseBot):
    """This is a template for bot class"""

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
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        #
        # Add your code here
        #

        # Do not delete this line:
        super().before_termination()

    #
    # Add your functions here
    #


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Template Bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = TemplateBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
