import os
import schedule
import functools
import time
import csv
import subprocess

from nebixbot.command_center.bot.base_bot import BaseBot
from nebixbot.api_client.bybit.client import (
    BybitClient,
    timestamp_to_datetime,
)
from nebixbot.api_client.bybit.enums import Symbol, Interval


class SampleBot(BaseBot):
    """This is Sample Bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")
        secret = "cByYSrsJCT4FAWcUjFvNU82Z0LmkTpVTKt2r"  # TODO: DELETE
        api_key = "6dVKPDrRUbDsCOtK0F"  # TODO: DELETE
        self.client = BybitClient(
            is_testnet=True,
            secret=secret,
            api_key=api_key,
            req_timeout=5,
        )
        # Rscript Install.R
        file_path = SampleBot.get_filepath("Install.R")
        self.run_r_code(file_path)
        # Install library
        lib_filepath = self.get_filepath("NebPackage/Neb_2.5.0.tar.gz")
        subprocess.Popen(f"R CMD INSTALL {lib_filepath}", shell=True)
        self.logger.info("Required packages for R installed.")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")
        try:
            self.trading_system()
            schedule.every(60).seconds.do(self.trading_system)
            # Do not delete these lines:
            while True:
                if not schedule.jobs:
                    self.logger.info("No jobs to run")
                    self.before_termination()
                schedule.run_pending()
                time.sleep(1)
        except Exception as err:
            self.logger.error(err)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")

        # Do not delete this line:
        super().before_termination()

    @staticmethod
    def get_filepath(filename):
        """Get module-related filepath"""
        return os.path.join(os.path.dirname(__file__), filename)

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
    def trading_system(self):
        """The main function for bot algorithm"""
        self.logger.info("running trading system...")
        symbol = Symbol.BTCUSD
        interval = Interval.i1
        filepath = SampleBot.get_filepath("Temp/Data.csv")
        self.get_kline_data(symbol, 200, interval, filepath)
        r_filepath = SampleBot.get_filepath("RunStrategy.R")
        self.run_r_code(r_filepath)

    def get_kline_data(self, symbol, limit, interval, filepath):
        """Get kline data"""
        if interval == Interval.Y:
            return
        (
            next_kline_ts,
            last_kline_ts,
            delta,
        ) = self.client.get_kline_open_timestamps(symbol, interval)
        from_ts = next_kline_ts - delta * limit
        from_ts = 0 if from_ts < 0 else from_ts
        from_dt = timestamp_to_datetime(from_ts)

        res = self.client.get_kline(symbol, interval, from_dt, limit)

        # if results exits in response:
        if res and "result" in res and res["result"]:
            self.logger.info(
                f"Writing kline csv results for symbol:{symbol}, " +
                f"interval:{interval}..."
            )
            results = [
                [
                    "Index",
                    "Open",
                    "Close",
                    "High",
                    "Low",
                    "Volume",
                    "TimeStamp",
                ]
            ]
            for count, kline in enumerate(res["result"][::-1]):
                results.append(
                    [
                        count + 1,
                        kline["open"],
                        kline["close"],
                        kline["high"],
                        kline["low"],
                        kline["volume"],
                        kline["open_time"],
                    ]
                )

            with open(filepath, "w+", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(results)
                self.logger.info("Successfully wrote results to file")

        else:
            self.logger.error(
                "Something was wrong with API response. "
                + f"The response was: {res}"
            )

    def run_r_code(self, filepath):
        """Run R language code in a new subprocess and return pid"""
        self.logger.info(f"running R code in: {filepath}")
        try:
            proc = subprocess.Popen(
                f"cd {self.get_filepath('')} && Rscript {filepath} --no-save",
                shell=True,
                preexec_fn=os.setsid,
            )
            self.logger.info(
                f"Successfully ran R code subprocess. (pid={proc.pid})"
            )
            return proc.pid
        except Exception as err:
            self.logger.error(
                f"Failed to ran R code subprocess. Error message: {err}"
            )
            return None


if __name__ == "__main__":
    try:
        # Change name and version of your bot:
        name = "Sample Bot"
        version = "1.1.0"
        # Do not delete these lines:
        bot = SampleBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
