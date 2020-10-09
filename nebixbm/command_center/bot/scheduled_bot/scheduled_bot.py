import schedule
import functools
import requests
import time

from nebixbm.command_center.bot.base_bot import BaseBot


name = "scheduled bot"
version = "1.0.0"


class ScheduledBot(BaseBot):
    """This is scheduled bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")
        schedule.every(10).seconds.do(self.ping_google)
        while True:
            if not schedule.jobs:
                self.logger.info("No jobs to run")
                self.before_termination()
            schedule.run_pending()
            time.sleep(1)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")

        super().before_termination()

    def catch_exceptions(cancel_on_failure=False):
        def catch_exceptions_decorator(job_func):
            @functools.wraps(job_func)
            def wrapper(self, *args, **kwargs):
                try:
                    return job_func(self, *args, **kwargs)
                except Exception as err:
                    self.logger.error(err)
                    if cancel_on_failure:
                        return schedule.CancelJob

            return wrapper

        return catch_exceptions_decorator

    @catch_exceptions(cancel_on_failure=True)
    def ping_google(self):
        r = requests.get("https://Google.com/")
        self.logger.info(f"Google server response: {r.status_code}")


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        global name 
        global version

        # Do not delete these lines:
        bot = ScheduledBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
