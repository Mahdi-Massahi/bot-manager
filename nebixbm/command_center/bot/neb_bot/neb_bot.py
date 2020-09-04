import os
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
    BinanceException,
)
import nebixbm.api_client.bybit.enums as bybit_enum
import nebixbm.api_client.binance.enums as binance_enum
from nebixbm.command_center.bot.sample_bot import enums
from nebixbm.command_center.tools.scheduler import (
    Job,
    c2s,
    timestamp_now,
    datetime_to_timestamp,
)
from nebixbm.command_center.tools.csv_validator import validate_two_csvfiles


class NebBot(BaseBot):
    """Neb bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        self.start_time = 0
        self.timeout_value = 120  # sec
        secret = "cByYSrsJCT4FAWcUjFvNU82Z0LmkTpVTKt2r"  # TODO: DELETE
        api_key = "6dVKPDrRUbDsCOtK0F"  # TODO: DELETE
        self.bybit_client = BybitClient(
            is_testnet=True, secret=secret, api_key=api_key, req_timeout=5,
        )
        self.binance_client = BinanceClient(
            secret="", api_key="", req_timeout=5,
        )
        self.redis = RedisDB()

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

        # Install library
        lib_filepath = self.get_filepath("NebPackage/Neb_2.5.0.tar.gz")
        command = f"R CMD INSTALL --no-lock {lib_filepath}"
        state_installation_neb = self.run_cmd_command(command, 30)

        # Run Install.R
        file_path = NebBot.get_filepath("Install.R")
        state_installation_reqs = self.run_r_code(file_path, 60 * 5)

        if state_installation_neb and state_installation_reqs:
            self.logger.info("Required packages for R are installed.")
        else:
            self.logger.critical("Installing required packages for R failed.")
            raise Exception("Nothing can go forward!")

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
        # Bot starting datetime
        start_dt = datetime.datetime(2020, 8, 30, 22, 58, 0)
        start_ts = datetime_to_timestamp(start_dt, is_utc=True)

        # Bot termination datetime (end)
        # end_dt = datetime.datetime(2021, 9, 1, 23, 59, 0)
        # end_ts = datetime_to_timestamp(end_dt, is_utc=True)

        # timestamp delta between each time trading system will run:
        schedule_delta_ts = c2s(minutes=1) * 1000  # x1000 to convert to mili
        # first job timestamp (current job):
        job_start_ts = start_ts
        if job_start_ts < timestamp_now():
            raise Exception(
                "Job start timestamp already has passed.\n"
                + f"job start time: {job_start_ts}\n"
                + f"now\t\t{timestamp_now()}"
            )
        # second job timestamp (next job):
        next_job_start_ts = job_start_ts + schedule_delta_ts
        self.logger.debug(f"Next job start-time set to {next_job_start_ts}")

        # buffered values
        opd = None  # Open Position Data
        nsg = False  # New Signal? as bool
        do_close_position = False  # close position or not
        do_open_position = False  # open position or not

        # trading system schedule loop:
        run_trading_system = True
        while run_trading_system:
            self.logger.debug(
                "Next job starts in "
                + f"{int(job_start_ts-timestamp_now())}ms"
            )
            try:
                # state no.02, no.03, no.04 - get markets klines
                if job_start_ts <= timestamp_now():
                    self.logger.info("[state-no.01]")
                    is_state_passed = self.get_markets_klines(
                        job_start_ts, schedule_delta_ts,
                    )
                    if not is_state_passed:
                        (
                            job_start_ts,
                            next_job_start_ts,
                        ) = self.skip_to_next_job(
                            next_job_start_ts, schedule_delta_ts
                        )
                    else:
                        self.logger.info("passed state no.02, no.03, no.04")

                # state no. 05 - Run strategy R code
                if job_start_ts <= timestamp_now():
                    self.logger.info("[state no.05]")
                    r_filepath = NebBot.get_filepath("RunStrategy.R")
                    is_state_passed = self.run_r_code(r_filepath, timeout=10)
                    if not is_state_passed:
                        raise Exception("Error running 'RunStrategy.R'.")
                    else:
                        self.logger.info("passed state no.05")

                # state no.06, no.07, no.08 - open position check
                if job_start_ts <= timestamp_now():
                    self.logger.info("[state-no.06]")
                    opd = self.get_open_position_data(
                        job_start_ts, schedule_delta_ts,
                    )
                    if opd is None:
                        (
                            job_start_ts,
                            next_job_start_ts,
                        ) = self.skip_to_next_job(
                            next_job_start_ts, schedule_delta_ts
                        )
                    else:
                        self.logger.info(opd)
                        self.logger.info("passed state no.06, no.07, no.08")

                # state no.09, no.10, and no.11
                if job_start_ts <= timestamp_now():
                    do_close_position = False
                    do_open_position = False
                    self.logger.info("[state-no.09]")
                    long_enter = self.get_redis_value(
                        enums.StrategyVariables.LongEntry
                    )
                    long_exit = self.get_redis_value(
                        enums.StrategyVariables.LongExit
                    )
                    short_enter = self.get_redis_value(
                        enums.StrategyVariables.ShortEntry
                    )
                    short_exit = self.get_redis_value(
                        enums.StrategyVariables.ShortExit
                    )
                    nsg = long_enter or long_exit or short_enter or short_exit
                    self.logger.info("passed state no.09")

                    if not nsg:
                        # there is no new signal
                        self.logger.debug("There is no new signal.")
                        (
                            job_start_ts,
                            next_job_start_ts,
                        ) = self.skip_to_next_job(
                            next_job_start_ts, schedule_delta_ts
                        )
                    else:
                        # there is a new signal
                        self.logger.debug("There is a new signal.")
                        # state no. 10 - check if there is an open position
                        self.logger.info("[state-no.10]")
                        if not opd["side"] == bybit_enum.Side.NONE:
                            self.logger.info("[state-no.11]")
                            # there is an open position
                            self.logger.debug("There is an open position.")
                            # TODO: ask Farzin what about exits?
                            if (
                                opd["side"] == bybit_enum.Side.BUY
                                and long_enter
                            ) or (
                                opd["side"] == bybit_enum.Side.SELL
                                and short_enter
                            ):
                                (
                                    job_start_ts,
                                    next_job_start_ts,
                                ) = self.skip_to_next_job(
                                    next_job_start_ts, schedule_delta_ts
                                )
                            else:
                                do_open_position = True
                                do_close_position = True
                                self.logger.debug(
                                    "Close the existing position" +
                                    "and Oen the new one"
                                )
                                self.logger.info("passed stage no.11")
                        else:
                            # there is no open position
                            self.logger.debug("There is no open position.")
                            do_open_position = True
                            do_close_position = False
                            self.logger.debug("Open the new position")
                        self.logger.info("passed state no.10")

                    # TODO: the rest

                # Code For Fun!
                # close position
                if do_close_position:
                    self.bybit_client.change_user_leverage(
                        bybit_enum.Symbol.BTCUSD, 100
                    )
                    self.logger.info("leverage changed to 1x.")

                    if opd[
                        "side"
                    ] == bybit_enum.Side.BUY and self.get_redis_value(
                        enums.StrategyVariables.LongExit
                    ):
                        self.logger.debug("Closing long position...")
                        tif = bybit_enum.TimeInForce.GOODTILLCANCEL
                        res = self.bybit_client.place_order(
                            side=bybit_enum.Side.SELL,
                            order_type=bybit_enum.OrderType.MARKET,
                            symbol=bybit_enum.Symbol.BTCUSD,
                            qty=opd["size"],
                            reduce_only=True,
                            time_in_force=tif,
                        )
                        self.logger.debug("Long position closed.")
                        self.logger.info(res)
                    if opd[
                        "side"
                    ] == bybit_enum.Side.SELL and self.get_redis_value(
                        enums.StrategyVariables.ShortExit
                    ):
                        self.logger.debug("Closing short position...")
                        tif = bybit_enum.TimeInForce.GOODTILLCANCEL
                        res = self.bybit_client.place_order(
                            side=bybit_enum.Side.BUY,
                            order_type=bybit_enum.OrderType.MARKET,
                            symbol=bybit_enum.Symbol.BTCUSD,
                            qty=opd["size"],
                            reduce_only=True,
                            time_in_force=tif,
                        )
                        self.logger.debug("Short position closed.")
                        self.logger.info(res)

                    do_close_position = False

                # open position
                if do_open_position:
                    self.bybit_client.change_user_leverage(
                        bybit_enum.Symbol.BTCUSD, 100
                    )
                    self.logger.info("leverage changed to 1x.")
                    size = self.bybit_client.get_wallet_balance(
                        bybit_enum.Coin.BTC
                    )["result"][bybit_enum.Coin.BTC]["wallet_balance"]
                    self.logger.info(f"Current balance size is {size}")

                    psm = self.get_redis_value(
                        enums.StrategyVariables.PositionSizeMultiplier
                    )
                    slp = self.get_redis_value(
                        enums.StrategyVariables.StopLossValue
                    )

                    if self.get_redis_value(
                        enums.StrategyVariables.LongEntry
                    ):
                        self.logger.debug("Opening long position...")
                        tif = bybit_enum.TimeInForce.GOODTILLCANCEL
                        res = self.bybit_client.place_order(
                            side=bybit_enum.Side.BUY,
                            order_type=bybit_enum.OrderType.MARKET,
                            symbol=bybit_enum.Symbol.BTCUSD,
                            qty=int(10 * psm),
                            stop_loss=slp,
                            time_in_force=tif,
                        )
                        self.logger.info("Long position opened.")

                    if self.get_redis_value(
                        enums.StrategyVariables.ShortEntry
                    ):
                        self.logger.debug("Opening short position...")
                        tif = bybit_enum.TimeInForce.GOODTILLCANCEL
                        res = self.bybit_client.place_order(
                            side=bybit_enum.Side.SELL,
                            order_type=bybit_enum.OrderType.MARKET,
                            symbol=bybit_enum.Symbol.BTCUSD,
                            qty=int(10 * psm),
                            stop_loss=slp,
                            time_in_force=tif,
                        )
                        self.logger.info("Short position opened.")

                    self.logger.info(res)
                    do_open_position = False

                    # skip to next schedule job:
                    job_start_ts = next_job_start_ts
                    next_job_start_ts = job_start_ts + schedule_delta_ts
                    self.logger.info("job scheduled for next bar.")
                    self.logger.info("[state-no.42]")

            except Exception as err:
                self.logger.critical(err)
                (job_start_ts, next_job_start_ts) = self.skip_to_next_job(
                    next_job_start_ts, schedule_delta_ts
                )
                # raise TODO: Remove it finally and handle the error

            time.sleep(5)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")

        # Do not delete this line:
        super().before_termination()

    @staticmethod
    def get_filepath(filename):
        """Get module-related filepath"""
        return os.path.join(os.path.dirname(__file__), filename)

    # TODO: move to client
    def get_bybit_kline(self, symbol, limit, interval, filepath):
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

    # TODO: move to client
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

    def run_r_code(self, filepath, timeout):
        """Run R language code in a new subprocess and return status"""
        self.logger.info(f"Running R code in: {filepath}")
        command = (
            f"cd {self.get_filepath('')} && Rscript {filepath} --no-save"
        )
        return self.run_cmd_command(command, timeout=timeout)

    def run_cmd_command(self, command, timeout):
        """Run CMD command in a new subprocess and return status"""
        self.logger.info(f"running cmd command: {command}")
        try:
            proc = subprocess.Popen(
                command,
                shell=True,
                preexec_fn=os.setsid,
                stdout=subprocess.PIPE,
            )
            out, error = proc.communicate(timeout=timeout)
            # proc.wait(timeout)
            if proc.returncode:
                raise Exception(
                    "Failed CMD command. "
                    + f"Return-code:{proc.returncode}. Error:{error}."
                )
            else:
                self.logger.info(
                    f"Successfully CMD command subprocess. (pid={proc.pid})"
                )
                return True
        except Exception as err:
            self.logger.error(
                "Failed to execute CMD command" +
                f"subprocess. Error message: {err}"
            )
            return False

    def get_redis_value(self, variable):
        value = self.redis.get(variable)
        if (
            variable == enums.StrategyVariables.LongEntry
            or variable == enums.StrategyVariables.LongExit
            or variable == enums.StrategyVariables.ShortEntry
            or variable == enums.StrategyVariables.ShortExit
        ):
            if value == "TRUE":
                return True
            elif value == "FALSE":
                return False
        elif (
            variable == enums.StrategyVariables.PositionSizeMultiplier
            or variable == enums.StrategyVariables.StopLossValue
        ):
            if value == "NA":
                return None
            else:
                return float(value)

    def get_orderbook(self):
        return NotImplementedError

    def get_last_traded_price(self):
        return NotImplementedError

    def get_markets_klines_func(self):
        """Get bybit and binance kline data"""

        # Bybit data:
        bybit_symbol = bybit_enum.Symbol.BTCUSD
        bybit_interval = bybit_enum.Interval.i1
        bybit_filepath = NebBot.get_filepath("Temp/tData.csv")
        bybit_data_success = self.get_bybit_kline(
            bybit_symbol, 200, bybit_interval, bybit_filepath
        )
        if not bybit_data_success:
            raise RequestException("failed to get data from Bybit")

        # Binance data
        binance_symbol = binance_enum.Symbol.BTCUSDT
        binance_interval = binance_enum.Interval.i1m
        binance_filepath = NebBot.get_filepath("Temp/aData.csv")
        binance_data_success = self.get_binance_kline(
            binance_symbol,
            binance_interval,
            limit=200,
            filepath=binance_filepath,
        )
        if not binance_data_success:
            raise RequestException("failed to get data from Binance")

    def get_markets_klines(self, job_start_ts, schedule_delta_ts):
        """Gets data and validates the retrieved files"""
        retrieve_data_timeout_ts = job_start_ts + int(
            schedule_delta_ts * 6 / 8
        )
        retrieve_data_job = Job(
            self.get_markets_klines_func, job_start_ts, []
        )
        while not retrieve_data_job.has_run:
            if retrieve_data_job.can_run():
                try:
                    # state no.04 - check schedule timeout:
                    self.logger.info("[state-no.04]")
                    if timestamp_now() > retrieve_data_timeout_ts:
                        self.logger.error(
                            "failed state no.04 - schedule timed out "
                            + f"(timeout ts:{retrieve_data_timeout_ts},"
                            + f" now:{timestamp_now()})"
                        )
                        return False

                    # state no.02 - get data
                    self.logger.info("[state-no.02]")
                    retrieve_data_job.run_now()
                    self.logger.info("passed state no.02 - got data")

                    # state no.03 - validation check
                    self.logger.info("[state-no.03]")
                    bybit_csv = self.get_filepath("Temp/tData.csv")
                    binance_csv = self.get_filepath("Temp/aData.csv")
                    validity_check, error = validate_two_csvfiles(
                        bybit_csv, binance_csv
                    )
                    if validity_check:
                        self.logger.info(
                            "passed state no.03 - data validated"
                        )
                    else:
                        self.logger.info(
                            "failed state no.03" +
                            f" - data validation error {error}"
                        )
                        raise RequestException()

                except RequestException as err:
                    self.logger.error(err)
                    retrieve_data_job.has_run = False
                    retry_after = 5  # seconds
                    self.logger.info(
                        "Retrying to get data after "
                        + f"{retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                except Exception as err:  # internal error happened:
                    raise Exception(err)

                else:  # passed all states:
                    return True
            self.logger.debug("retrying to see if job can run")
            time.sleep(5)

    def get_open_position_data(self, job_start_ts, schedule_delta_ts):
        """Gets open position data and returns it"""
        retrieve_data_timeout_ts = job_start_ts + int(
            schedule_delta_ts * 6 / 8
        )
        retrieve_data_job = Job(
            self.bybit_client.get_position,
            job_start_ts,
            [bybit_enum.Symbol.BTCUSD],
        )
        while not retrieve_data_job.has_run:
            if retrieve_data_job.can_run():
                try:
                    # state no.08 - check schedule timeout:
                    self.logger.info("[state-no.08]")
                    if timestamp_now() > retrieve_data_timeout_ts:
                        self.logger.error(
                            "failed state no.08 - schedule timed out "
                            + f"(timeout ts:{retrieve_data_timeout_ts},"
                            + f" now:{timestamp_now()})"
                        )
                        return None

                    # state no.06 - get data
                    self.logger.info("[state-no.06]")
                    opd = retrieve_data_job.run_now()
                    self.logger.info("passed state no.06 - got data")

                    # state no.07 - validation check
                    self.logger.info("[state-no.07]")
                    if not str(opd["ret_code"]) == "0":
                        self.logger.info("validity check error.")
                        raise RequestException("ret_code status is not 0.")
                    self.logger.info("passed state no.07 - validity checked")

                    return opd["result"]

                except RequestException as err:
                    self.logger.error(err)
                    retrieve_data_job.has_run = False
                    retry_after = 5  # seconds
                    self.logger.info(
                        "Retrying to get data after "
                        + f"{retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                except Exception as err:  # internal error happened:
                    raise Exception(err)

            self.logger.debug("retrying to see if job can run")
            time.sleep(5)

    def skip_to_next_job(
            self, next_job_start_ts, schedule_delta_ts
    ):
        """Skips to next schedule job"""
        job_start_ts = next_job_start_ts
        next_job_start_ts = job_start_ts + schedule_delta_ts
        self.logger.info(
            "skipping to next schedule job"
            + f" (now:{timestamp_now},"
            + f" current jobs ts:{job_start_ts})"
        )
        self.logger.info("[state-no.42]")
        return job_start_ts, next_job_start_ts


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Neb Bot"
        version = "0.3.45"

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
