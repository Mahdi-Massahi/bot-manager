import os

from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.command_center.notification.email import EmailSender


class NotifBot(BaseBot):
    """NotifBot to send notification!"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        email = os.getenv("NOTIFY_EMAIL")
        paswd = os.getenv("NOTIFY_PASS")
        smtp_host = os.getenv("EMAIL_SMTP_HOST")
        self.notifier = EmailSender(
            email,
            paswd,
            smtp_host
        )

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.debug("inside start()")
        sent = self.notifier.send_email(
            "nebixtest@gmail.com",
            "From Notify Bot!",
            "Okay, Okay... Go!"
        )
        if sent:
            self.logger.info("Successfully sent email")
        else:
            self.logger.error("Failed to send email")

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.debug("inside before_termination()")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Notif Bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = NotifBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
