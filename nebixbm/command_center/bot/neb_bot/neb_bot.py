import os
import schedule
import functools
import time
import csv
import subprocess
import datetime
from requests import RequestException

from nebixbm.database.driver import RedisDB
from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import (
    BybitClient,
    timestamp_to_datetime,
)
from nebixbm.api_client.binance.client import (
    BinanceClient,
)
import nebixbm.api_client.bybit.enums as bybit_enum
import nebixbm.api_client.binance.enums as binance_enum
from nebixbm.command_center.bot.sample_bot import enums
from nebixbm.command_center.tools.scheduler import Job, c2s, timestamp_now


class NebBot(BaseBot):
    """This is a template for bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        self.start_time = 0
        self.timeout_value = 120  # sec
        secret = "cByYSrsJCT4FAWcUjFvNU82Z0LmkTpVTKt2r"  # TODO: DELETE
        api_key = "6dVKPDrRUbDsCOtK0F"  # TODO: DELETE
        self.bybit_client = BybitClient(
            is_testnet=True,
            secret=secret,
            api_key=api_key,
            req_timeout=5,
        )
        self.binance_client = BinanceClient(
            secret="", api_key="", req_timeout=5,
        )
        self.redis = RedisDB()

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

        # Rscript Install.R
        file_path = NebBot.get_filepath("Install.R")
        self.run_r_code(file_path)

        # Install library
        lib_filepath = self.get_filepath("NebPackage/Neb_2.5.0.tar.gz")
        subprocess.Popen(f"R CMD INSTALL {lib_filepath}", shell=True)
        self.logger.info("Required packages for R are installed.")

        # Redis initialize
        self.redis.set(enums.StrategyVariables.EX_Done, "0")
        self.redis.set(enums.StrategyVariables.PP_Done, "0")
        self.redis.set(enums.StrategyVariables.StopLossValue, "NA")
        self.redis.set(enums.StrategyVariables.TimeCalculated, "NA")
        self.redis.set(enums.StrategyVariables.LongEntry, "FALSE")
        self.redis.set(enums.StrategyVariables.ShortEntry, "FALSE")
        self.redis.set(enums.StrategyVariables.LongExit, "FALSE")
        self.redis.set(enums.StrategyVariables.ShortExit, "FALSE")
        self.redis.set(enums.StrategyVariables.PositionSizeMultiplier, "NA")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")

        # TODO: set start datetime and end datetime for bot:
        start_dt = datetime.datetime(2020, 8, 24, 23, 50)
        end_dt = datetime.datetime(2022, 8, 24, 23, 50)

        # Schedule started:

        # state no.01 - start timer (set timer)
        self.logger.info("Started state no.01")

        # TODO: set these below:
        # WARNING: all timestamps should be in milliseconds
        # schedule_delta_ts time between schedules? (4 hours)
        # job_start_ts = 0
        # next_job_start_ts = 0

        # state no.02, no.03, no.04 - Get data and Validation and Timeout
        retrieve_data_timeout_ts = job_start_ts + int(schedule_delta_ts * 6 / 8)
        retrieve_data_job = Job(self.get_data, job_start_ts, [])
        while not retrieve_data_job.has_run:
            if retrieve_data_job.can_run():
                try:
                    retrieve_data_job.run_now()
                    # TODO: check data validation
                    # TODO: failed validation log err
                # Timeout error:
                except RequestException as err:
                    self.logger.error(err)
                    if not timestamp_now() <= retrieve_data_timeout_ts:
                        retrieve_data_job.has_run = False
                        retry_after = 4  # seconds
                        self.logger.info(f"Retrying to get data after {retry_after} seconds...")
                        time.sleep(retry_after)
                    else:
                        self.logger.error("Failed to retry to get data klines - failed state no.04")
                        # TODD: got to next shcedule job
                except Exception as err:
                    self.logger.error(err)
                    # TODO: bas eshia, function return true or set a boolean flag
                else:
                    self.logger.info("Successfully got data - passed state no.02, no.03, no.04")
            time.sleep(1)

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

    # @catch_exceptions(cancel_on_failure=True)
    def trading_system(self):
        """The main function for bot algorithm"""
        self.logger.info("running trading system...")
        #
        # # state no. 01 - start
        # self.start_time = time.time()
        # self.logger.info("Strategy state no. 01")
        #
        # # state no. 02 - Get data
        # # Bybit data
        # bybit_symbol = bybit_enum.Symbol.BTCUSD
        # bybit_interval = bybit_enum.Interval.i5
        # bybit_filepath = NebBot.get_filepath("Temp/Data.csv")
        #
        # bybit_get_res, binance_get_res, csv_validity_check = 3 * [False]
        #
        # while not (bybit_get_res and binance_get_res and csv_validity_check and self.check_timeouted()):
        #     # Get Bybit data
        #     bybit_get_res = self.get_kline_data(
        #         bybit_symbol,
        #         200,
        #         bybit_interval,
        #         bybit_filepath
        #     )
        #
        #     # Get Binance data
        #     # TODO: Get Binance data
        #     binance_get_res = True
        #
        #     # state no. 03 - got and validity check
        #     # TODO: Validity check .csv files
        #     csv_validity_check = self.check_csv_validity()
        #
        #     # state no. 04
        #     self.check_timeouted()

        # state no. 05 - Run strategy
        r_filepath = NebBot.get_filepath("RunStrategy.R")
        self.run_r_code(r_filepath)

        while True:
            try:
                # state no. 06 - Get open position data
                open_position_data = self.get_open_position_data()
                # state no. 07 - Got and valid
                break

            except Exception:
                # state no. 08 - Check timeout
                if not (self.check_timeouted()):
                    pass

        # state no. 09 - check if there is a new signal
        long_enter = self.get_redis_value(enums.StrategyVariables.LongEntry)
        long_exit = self.get_redis_value(enums.StrategyVariables.LongExit)
        short_enter = self.get_redis_value(enums.StrategyVariables.ShortEntry)
        short_exit = self.get_redis_value(enums.StrategyVariables.ShortExit)
        if not (long_enter or long_exit or short_enter or short_exit):
            # state no. 10 - check if is there an open position
            if open_position_data.list is None:
                pass
            else:
                # state no. 11
                side = enums.Side.NA
                if long_enter:
                    side = enums.Side.Long
                elif short_enter:
                    side = enums.Side.Short
                if open_position_data.side != side:
                    while True:
                        try:
                            # state no. 12
                            # orderbook = self.get_orderbook()
                            # last_traded_price = self.get_last_traded_price()
                            # state no.  13 - got and valid
                            break

                        except Exception:
                            # state no. 14 - Check timeout
                            if not (self.check_timeouted()):
                                pass

                    # state no. 15 - Liq. Cal.
                else:
                    self.end()
        else:
            self.end()

    def get_kline_data(self, symbol, limit, interval, filepath):
        """Get kline data"""
        if interval == bybit_enum.Interval.Y:
            return None
        (
            next_kline_ts,
            last_kline_ts,
            delta,
        ) = self.bybit_client.get_kline_open_timestamps(symbol, interval)
        from_ts = next_kline_ts - delta * limit
        from_ts = 0 if from_ts < 0 else from_ts
        from_dt = timestamp_to_datetime(from_ts)

        res = self.bybit_client.get_kline(symbol, interval, from_dt, limit)

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
            for count, kline in enumerate(res["result"]):
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
                return True

        else:
            self.logger.error(
                "Something was wrong with API response. "
                + f"The response was: {res}"
            )
            return False

    def get_binance_kline(self, symbol, interval, limit, filepath):
        klines = self.binance_client.get_kline(symbol, interval, limit=limit)
        if klines:
            self.logger.info(
                f"Writing kline csv results for symbol:{symbol}, "
                + f"interval:{interval}..."
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
            for c, k in enumerate(klines):
                results.append(
                    [c + 1, k[1], k[4], k[2], k[3], k[5], int(k[0] / 1000)]
                )

            with open(filepath, "w+", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(results)
                self.logger.info("Successfully wrote results to file")

        else:
            self.logger.error(
                "Something was wrong with API response. "
                + f"The response was: {klines}"
            )
            return False
        return True

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

    # def check_timeouted(self):
    #     if time.time() - self.start_time > self.timeout_value:
    #         self.logger.error("Time outed.")
    #         self.end()
    #         return True
    #     else:
    #         return False

    def check_csv_validity(self):
        return True

    def get_open_position_data(self):
        return NotImplementedError  # Position data obj.

    def get_redis_value(self, variable):
        return NotImplementedError

    def get_orderbook(self):
        return NotImplementedError

    def get_last_traded_price(self):
        return NotImplementedError

    def get_data(self):
        """Get bybit and binance kline data"""

        # Bybit data:
        bybit_symbol = bybit_enum.Symbol.BTCUSD
        bybit_interval = bybit_enum.Interval.i5
        bybit_filepath = NebBot.get_filepath("Temp/tData.csv")
        bybit_data_success = self.get_kline_data(
            bybit_symbol,
            200,
            bybit_interval,
            bybit_filepath
        )
        if not bybit_data_success:
            raise Exception("Failed to get data from Bybit")

        # Binance data
        binance_symbol = binance_enum.Symbol.BTCUSDT
        binance_interval = binance_enum.Interval.i5m
        binance_filepath = NebBot.get_filepath("Temp/aData.csv")
        binance_data_success = self.get_binance_kline(
            binance_symbol,
            binance_interval,
            limit=200,
            filepath=binance_filepath,
        )
        if not binance_data_success:
            raise Exception("Failed to get data from Binance")

        # state no. 03 - got and validity check
        # TODO: Validity check .csv files
        # csv_validity_check = self.check_csv_validity()


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
        if bot:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
