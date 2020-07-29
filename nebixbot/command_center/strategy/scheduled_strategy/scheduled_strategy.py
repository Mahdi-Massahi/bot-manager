import schedule
import functools
import requests
import time

from nebixbot.command_center.strategy.base_strategy import BaseStrategy


class ScheduledStrategy(BaseStrategy):
    """This is scheduled strategy class"""

    def __init__(self, name, version):
        """Init with name and version"""
        super().__init__(name, version)

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
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
        """Strategy Manager calls this before terminating a running strategy"""
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
        r = requests.get('https://Google.com/')
        self.logger.info(f'Google server response: {r.status_code}')


if __name__ == '__main__':
    try:

        # Change name and version of your strategy:
        name = 'scheduled strategy'
        version = '1.0.0'

        # Do not delete these lines:
        strategy = ScheduledStrategy(name, version)
        strategy.logger.info("Successfully initialized strategy")
        strategy.before_start()
        strategy.start()
    except Exception as err:
        if strategy is not None:
            strategy.logger.error(err)
            if not strategy.has_called_before_termination:
                strategy.before_termination()
