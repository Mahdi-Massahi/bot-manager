import os
import time
import subprocess
# import datetime
from requests import RequestException

from nebixbm.database.driver import RedisDB
from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import (
    BybitClient,
    # timestamp_to_datetime,
    # BybitException,
)
from nebixbm.api_client.binance.client import (
    BinanceClient,
    # BinanceException,
)
import nebixbm.api_client.bybit.enums as bybit_enum
import nebixbm.api_client.binance.enums as binance_enum
from nebixbm.command_center.bot.sample_bot import enums
from nebixbm.command_center.tools.scheduler import (
    Job,
    c2s,
    timestamp_now,
    # datetime_to_timestamp,
)
from nebixbm.command_center.tools.csv_validator import (
    csv_kline_validator,
    validate_two_csvfiles,
)


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

        # Algo. values
        self.TIMEOUT_TO_TIMEFRAME_RATIO = 0.98  # percent

        # timestamp delta between each time trading system will run:
        self.SCHEDULE_DELTA_TIME = c2s(minutes=1) * 1000

        # Get kline properties
        self.BYBIT_SYMBOL = bybit_enum.Symbol.BTCUSD
        self.BYBIT_INTERVAL = bybit_enum.Interval.i1
        self.BYBIT_LIMIT = 200
        self.BINANCE_SYMBOL = binance_enum.Symbol.BTCUSDT
        self.BINANCE_INTERVAL = binance_enum.Interval.i1m
        self.BINANCE_LIMIT = 200
        self.GET_KLINE_RETRY_DELAY = 5  # seconds

        self.state_flag = 0

        self.RUN_R_STRATEGY_TIMEOUT = 10  # seconds
        self.GET_ORDERBOOK_RETRY_DELAY = 10  # seconds

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

        # Run Install.R
        file_path = NebBot.get_filepath("Install.R")
        state_installation_reqs = self.run_r_code(file_path, 60 * 15)

        # Install library
        lib_filepath = self.get_filepath("NebPackage/Neb_2.5.0.tar.gz")
        command = f"R CMD INSTALL --no-lock {lib_filepath}"
        state_installation_neb = self.run_cmd_command(command, 60 * 1)

        if state_installation_neb and state_installation_reqs:
            self.logger.info("Required packages for R are installed.")
        else:
            self.logger.critical("Installing required packages for R failed.")
            raise Exception("Nothing can go forward!")

        # initialize redis values
        self.redis_value_reset()

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")

        # TODO: set start datetime and end datetime for bot:
        # Bot starting datetime
        # start_dt = datetime.datetime(2020, 9, 4, 16, 25, 0)
        # start_ts = datetime_to_timestamp(start_dt, is_utc=True)

        start_ts = timestamp_now() + 50

        # Bot termination datetime (end)
        # end_dt = datetime.datetime(2021, 9, 1, 23, 59, 0)
        # end_ts = datetime_to_timestamp(end_dt, is_utc=True)

        # first job timestamp (current job):
        job_start_ts = start_ts
        if job_start_ts < timestamp_now():
            raise Exception(
                "Job start timestamp already has passed.\n"
                + f"job start time: {job_start_ts}\n"
                + f"now\t\t{timestamp_now()}"
            )
        # TODO: uncomment above finally

        next_job_start_ts = job_start_ts + self.SCHEDULE_DELTA_TIME
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
                # TODO: use flags for making sure if conditions are checked
                # state no.02, no.03, no.04 - Get markets klines
                if job_start_ts <= timestamp_now() and self.state_flag == 0:
                    # Reset redis values TODO: Not sure if its true
                    self.redis_value_reset()

                    self.logger.info("[state-no.01]")
                    is_state_passed = self.get_markets_klines(
                        job_start_ts, self.SCHEDULE_DELTA_TIME,
                    )
                    if not is_state_passed:
                        (
                            job_start_ts,
                            next_job_start_ts,
                        ) = self.skip_to_next_job(
                            next_job_start_ts, self.SCHEDULE_DELTA_TIME
                        )
                    else:
                        self.logger.debug("Passed state no.02, no.03, no.04")
                        self.state_flag = 4

                # state no.05 - Run strategy R code
                if job_start_ts <= timestamp_now() and self.state_flag == 4:
                    self.logger.info("[state no.05]")
                    r_filepath = NebBot.get_filepath("RunStrategy.R")
                    is_state_passed = self.run_r_code(
                        filepath=r_filepath,
                        timeout=self.RUN_R_STRATEGY_TIMEOUT,
                    )
                    if not is_state_passed:
                        raise Exception("Error running 'RunStrategy.R'.")
                    else:
                        self.logger.debug("Passed state no.05")
                        self.state_flag = 5

                # state no.06, no.07, no.08 - open position check
                if job_start_ts <= timestamp_now() and self.state_flag == 5:
                    opd = self.get_open_position_data(
                        job_start_ts, self.SCHEDULE_DELTA_TIME, state_no=6
                    )
                    if opd is None:
                        (
                            job_start_ts,
                            next_job_start_ts,
                        ) = self.skip_to_next_job(
                            next_job_start_ts, self.SCHEDULE_DELTA_TIME
                        )
                    else:
                        self.logger.info("Passed state no.06, no.07, no.08")
                        (
                            job_start_ts,
                            next_job_start_ts,
                        ) = self.skip_to_next_job(
                            next_job_start_ts, self.SCHEDULE_DELTA_TIME
                        )
                        # self.state_flag = 8

                # state no.09, no.10, and no.11
                if job_start_ts <= timestamp_now() and self.state_flag == 8:
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
                            next_job_start_ts, self.SCHEDULE_DELTA_TIME
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
                                    next_job_start_ts,
                                    self.SCHEDULE_DELTA_TIME,
                                )
                            else:
                                do_open_position = True
                                do_close_position = True
                                self.logger.debug(
                                    "Close the existing position and"
                                    + " Oen the new one"
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
                    next_job_start_ts = (
                        job_start_ts + self.SCHEDULE_DELTA_TIME
                    )
                    self.logger.info("job scheduled for next bar.")
                    self.logger.info("[state-no.42]")

            except Exception as err:
                self.logger.critical(err)
                (job_start_ts, next_job_start_ts) = self.skip_to_next_job(
                    next_job_start_ts, self.SCHEDULE_DELTA_TIME
                )
                # raise TODO: Remove it finally and handle the error

            time.sleep(5)  # TODO: increase it finally to 0.5.

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")

        # Do not delete this line:
        super().before_termination()

    @staticmethod
    def get_filepath(filename):
        """Get module-related filepath"""
        return os.path.join(os.path.dirname(__file__), filename)

    # CHECKED
    def run_r_code(self, filepath, timeout):
        """Run R language code in a new subprocess and return status"""
        self.logger.debug(f"Running R code in: {filepath}")
        command = (
            f"cd {self.get_filepath('')} && Rscript {filepath} --no-save"
        )
        return self.run_cmd_command(command, timeout=timeout)

    # CHECKED
    def run_cmd_command(self, command, timeout):
        """Run CMD command in a new subprocess and return status"""
        self.logger.debug(f"Running cmd command: {command}")
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
                    + f"Return-code:{proc.returncode}."
                    + " Error:{error}."
                )
            else:
                self.logger.debug(
                    f"Successfully CMD command subprocess. (pid={proc.pid})"
                )
                return True
        except Exception as err:
            self.logger.error(
                "Failed to execute CMD command "
                + f"subprocess. Error message: {err}"
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

    # CHECKED
    def get_markets_klines_func(self):
        """Get bybit and binance kline data"""

        # Bybit data:
        self.logger.debug("Getting Bybit data...")
        bybit_filepath = NebBot.get_filepath("Temp/tData.csv")
        bybit_data_success = self.bybit_client.kline_to_csv(
            symbol=self.BYBIT_SYMBOL,
            limit=self.BYBIT_LIMIT,
            interval=self.BYBIT_INTERVAL,
            filepath=bybit_filepath,
        )
        if not bybit_data_success:
            raise RequestException("Failed to get data from Bybit.")

        # Binance data
        self.logger.debug("Getting Binance data...")
        binance_filepath = NebBot.get_filepath("Temp/aData.csv")
        binance_data_success = self.binance_client.kline_to_csv(
            symbol=self.BINANCE_SYMBOL,
            limit=self.BINANCE_LIMIT,
            interval=self.BINANCE_INTERVAL,
            filepath=binance_filepath,
        )
        if not binance_data_success:
            raise RequestException("Failed to get data from Binance.")

    # CHECKED
    def get_markets_klines(self, job_start_ts, schedule_delta_ts):
        """Gets data and validates the retrieved files"""
        retrieve_data_timeout_ts = job_start_ts + int(
            schedule_delta_ts * self.TIMEOUT_TO_TIMEFRAME_RATIO
        )
        retrieve_data_job = Job(
            self.get_markets_klines_func, job_start_ts, []
        )
        while not retrieve_data_job.has_run:
            if retrieve_data_job.can_run():
                try:
                    # state no.02 - check schedule timeout:
                    self.logger.info("[state-no.02]")
                    if timestamp_now() > retrieve_data_timeout_ts:
                        self.logger.error(
                            "Failed state no.02 - schedule timed out "
                            + f"(timeout ts:{retrieve_data_timeout_ts},"
                            + f" now:{timestamp_now()})"
                        )
                        return False

                    # state no.03 - get data
                    self.logger.info("[state-no.03]")
                    retrieve_data_job.run_now()
                    self.logger.debug("passed state no.03 - got data")

                    # state no.04 - validation check
                    self.logger.info("[state-no.04]")
                    bybit_csv_path = self.get_filepath("Temp/tData.csv")
                    binance_csv_path = self.get_filepath("Temp/aData.csv")

                    # Checking files individually
                    (
                        is_binance_csv_checked,
                        binance_csv_msg,
                    ) = csv_kline_validator(binance_csv_path)
                    (
                        is_bybit_csv_checked,
                        bybit_csv_msg,
                    ) = csv_kline_validator(bybit_csv_path)

                    if not is_binance_csv_checked:
                        self.logger.error(
                            "Failed state no.04 - "
                            + "Binance csv validity " +
                            f"check error {binance_csv_msg}"
                        )
                        raise RequestException(
                            "Binance csv validation failed."
                        )
                    else:
                        if binance_csv_msg:
                            self.logger.debug(
                                "Binance csv contains kline(s)" +
                                " with zero volume."
                            )

                    if not is_bybit_csv_checked:
                        self.logger.error(
                            "Failed state no.04 - "
                            + f"Bybit csv validity check error {bybit_csv_msg}"
                        )
                        raise RequestException("Bybit csv validation failed.")
                    else:
                        if bybit_csv_msg:
                            self.logger.debug(
                                "Bybit csv contains kline(s) with zero volume."
                            )

                    # Check both files at once
                    validity_check, error = validate_two_csvfiles(
                        binance_csv_path, bybit_csv_path
                    )
                    if validity_check:
                        self.logger.debug(
                            "Successfully checked Binance and Bybit csv" +
                            " files synchronization."
                        )
                    else:
                        raise RequestException(
                            "Failed Binance and Bybit csv files" +
                            " synchronization check."
                        )

                except RequestException as err:
                    self.logger.error(err)
                    retrieve_data_job.has_run = False
                    retry_after = self.GET_KLINE_RETRY_DELAY
                    self.logger.info(
                        "Retrying to get data after "
                        + f"{retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                except Exception as ex:
                    self.logger.critical(ex)
                    raise
                else:
                    self.logger.debug("Passed states no.04.")
                    return True

                self.logger.debug("Retrying to see if job can run.")

    # CHECKED???
    def get_open_position_data(
        self, job_start_ts, schedule_delta_ts, state_no
    ):
        """Gets open position data and returns it"""
        retrieve_data_timeout_ts = job_start_ts + int(
            schedule_delta_ts * self.TIMEOUT_TO_TIMEFRAME_RATIO
        )
        retrieve_data_job = Job(
            self.bybit_client.get_position, job_start_ts, [self.BYBIT_SYMBOL],
        )
        while not retrieve_data_job.has_run:
            if retrieve_data_job.can_run():
                try:
                    # state no.{state_no} - check schedule timeout:
                    self.logger.info(f"[state-no.{str(state_no).zfill(2)}]")
                    if timestamp_now() > retrieve_data_timeout_ts:
                        self.logger.error(
                            f"Failed state no.{str(state_no).zfill(2)}" + " "
                            "- schedule timed out "
                            + f"(timeout ts:{retrieve_data_timeout_ts},"
                            + f" now:{timestamp_now()})"
                        )
                        return None

                    # state no.{state_no+1} - get data
                    self.logger.info(f"[state-no.{str(state_no+1).zfill(2)}]")
                    opd = retrieve_data_job.run_now()
                    self.logger.info(
                        f"Passed state no.{str(state_no+1).zfill(2)}"
                        + " - got open position data"
                    )

                    # state no.{state_no+2} - validation check
                    self.logger.info(f"[state-no.{str(state_no+2).zfill(2)}]")
                    if not str(opd["ret_code"]) == "0":
                        self.logger.info("validity check error.")
                        raise RequestException(
                            "Failed validity check - "
                            + "ret_code status is not 0."
                        )
                    self.logger.info(
                        f"Passed state no.{str(state_no+2).zfill(2)}"
                        + " - validity checked"
                    )
                    self.logger.info(
                        f'Current position data: {opd["result"]}'
                    )
                    return opd["result"]

                except RequestException as err:
                    self.logger.error(err)
                    retrieve_data_job.has_run = False
                    retry_after = self.GET_ORDERBOOK_RETRY_DELAY
                    self.logger.info(
                        "Retrying to get data after "
                        + f"{retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                except Exception as ex:
                    self.logger.critical(ex)
                    raise Exception(ex)

                self.logger.debug("Retrying to see if job can run.")

    # CHECKED
    def skip_to_next_job(self, next_job_start_ts, schedule_delta_ts):
        """Skips to next schedule job"""
        job_start_ts = next_job_start_ts
        next_job_start_ts = job_start_ts + schedule_delta_ts
        self.logger.info(
            "skipping to next schedule job"
            + f" (now:{timestamp_now},"
            + f" current jobs ts:{job_start_ts})"
        )
        self.logger.info("[state-no.42]")
        self.state_flag = 0
        return job_start_ts, next_job_start_ts

    # CHECKED
    def redis_value_reset(self):
        """Reset the strategy out-put values in redis"""
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


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Neb Bot"
        version = "0.3.55"

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
