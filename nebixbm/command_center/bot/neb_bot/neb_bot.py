import os
import time
import subprocess
import datetime
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
    datetime_to_timestamp,
)
from nebixbm.command_center.tools.csv_validator import (
    csv_kline_validator,
    validate_two_csvfiles,
)


class CustomException(Exception):
    pass


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
        self.TIMEOUT_TO_TIMEFRAME_RATIO = 0.90  # percent

        # timestamp delta between each time trading system will run:
        self.T_ALGO_INTERVAL = 1  # in minutes
        self.SCHEDULE_DELTA_TIME = c2s(minutes=self.T_ALGO_INTERVAL) * 1000
        # 5: seconds for cleanup
        self.T_ALGO_TIMEOUT_DURATION = (
                c2s(minutes=self.T_ALGO_INTERVAL) *
                self.TIMEOUT_TO_TIMEFRAME_RATIO)

        # Get kline properties
        self.BYBIT_SYMBOL = bybit_enum.Symbol.BTCUSD
        self.BYBIT_INTERVAL = bybit_enum.Interval.i1
        self.BYBIT_LIMIT = 200
        self.BINANCE_SYMBOL = binance_enum.Symbol.BTCUSDT
        self.BINANCE_INTERVAL = binance_enum.Interval.i1m
        self.BINANCE_LIMIT = 200
        self.GET_KLINE_RETRY_DELAY = 5  # seconds

        self.RUN_R_STRATEGY_TIMEOUT = 10  # seconds
        self.GET_ORDERBOOK_RETRY_DELAY = 10  # seconds

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.debug("inside before_start()")
        self.logger.info("[state-no:1.02]")

        # Run Install.R
        file_path = NebBot.get_filepath("Install.R")
        state_installation_reqs = self.run_r_code(file_path, 60 * 15)

        # Install library
        lib_filepath = self.get_filepath("NebPackage/Neb_2.5.0.tar.gz")
        command = f"R CMD INSTALL --no-lock {lib_filepath}"
        state_installation_neb = self.run_cmd_command(command, 60 * 1)

        if state_installation_neb and state_installation_reqs:
            self.logger.debug("Required packages for R are installed.")
        else:
            self.logger.critical("Installing required packages for R failed.")
            raise Exception("Nothing can go forward!")

        # initialize redis values
        self.redis_value_reset()

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.debug("inside start()")
        self.logger.info("[state-no:2.01]")

        # TODO: set start datetime and end datetime for bot:
        # Bot starting datetime
        # start_dt = datetime.datetime(2020, 9, 4, 16, 25, 0)
        # start_ts = datetime_to_timestamp(start_dt, is_utc=True)

        start_ts = timestamp_now() + 50

        # Bot termination datetime (end)
        end_dt = datetime.datetime(2021, 9, 1, 23, 59, 0)
        end_ts = datetime_to_timestamp(end_dt, is_utc=True)

        # first job timestamp (current job):
        job_start_ts = start_ts
        if job_start_ts < timestamp_now():
            raise Exception(
                "Job start timestamp already has passed.\n"
                + f"job start time: {job_start_ts}\n"
                + f"now\t\t{timestamp_now()}"
            )

        # trading system schedule loop:
        run_trading_system = True
        while run_trading_system:
            if end_ts <= timestamp_now():
                self.logger.info("[state-no:3.??]")
                self.logger.debug("Reached Bot end time.")
                # TODO Notify the end of bot life
                run_trading_system = False

            if job_start_ts <= timestamp_now() and run_trading_system:
                self.logger.info("[state-no:2.02]")
                try:
                    res = self.run_with_timeout(
                        self.trading_algo,
                        None,
                        self.T_ALGO_TIMEOUT_DURATION,
                        self.Result.TIMED_OUT
                    )
                    if res == self.Result.TIMED_OUT:
                        self.logger.warning("Schedule timed out.")
                    elif res == self.Result.FAIL:
                        raise CustomException("Schedule failed.")
                    elif res == self.Result.SUCCESS:
                        self.logger.debug("Successfully ran job.")
                    job_start_ts += self.SCHEDULE_DELTA_TIME

                except Exception as err:
                    self.logger.info("[state-no:3.01]")
                    self.logger.critical("Something very bad has happened.")
                    self.logger.exception(err)
                    self.before_termination()

            # TODO: Remove bellow finally
            self.logger.debug(
                "Next job starts in "
                + f"{int(job_start_ts - timestamp_now())}ms"
            )
            time.sleep(5)  # TODO: change it finally to 0.5.

    def trading_algo(self, do_state=3):
        """"TRADING ALGO.: returns only success or fail from result class"""
        if do_state == 3:
            self.redis_value_reset()
            self.get_markets_klines()
            self.run_r_strategy()

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.debug("inside before_termination()")
        self.logger.info("[state-no:3.01]")

        # Do not delete this line:
        super().before_termination()

    @staticmethod
    def get_filepath(filename):
        """Get module-related filepath"""
        return os.path.join(os.path.dirname(__file__), filename)

    # DOUBLE CHECKED
    def run_r_code(self, filepath, timeout):
        """Run R language code in a new subprocess
        Returns a status as True or False
        Raises no Exception"""
        self.logger.debug(f"Running R code in: {filepath}")
        command = (
            f"cd {self.get_filepath('')} && Rscript {filepath} --no-save"
        )
        return self.run_cmd_command(command, timeout=timeout)

    # DOUBLE CHECKED
    def run_cmd_command(self, command, timeout):
        """Run CMD command in a new subprocess
        Returns a status as True or False
        Raises no Exception"""
        self.logger.debug(f"Running cmd command: {command}")
        try:
            proc = subprocess.Popen(
                command,
                shell=True,
                preexec_fn=os.setsid,
                stdout=subprocess.PIPE,
            )
            out, error = proc.communicate(timeout=timeout)
            if proc.returncode:
                raise CustomException(
                    f"Return-code:{proc.returncode}. " +
                    f"Error:{error}."
                )
            else:
                self.logger.debug(
                    f"Successfully CMD command subprocess. (pid={proc.pid})"
                )
                return True
        except Exception as ex:
            self.logger.error(
                "Failed to execute CMD command " +
                f"subprocess. Error message: {ex}"
            )
            return False

    # DOUBLE CHECKED
    def get_r_strategy_output(self, variable):
        """Converts R strategy result values to python readable values
        Returns the corresponding value in redis
        Raises Exception on non-strategy-value requests"""
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
        else:
            raise Exception("Not a valid strategy value.")

    def get_orderbook(self):
        raise NotImplementedError

    def get_last_traded_price(self):
        raise NotImplementedError

    # DOUBLE CHECKED
    def get_markets_klines_func(self):
        """Get bybit and binance kline data
        Returns nothing
        Raises CustomException, Exception, and Request Exceptions"""

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
            raise CustomException("Failed to get data from Bybit.")

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
            raise CustomException("Failed to get data from Binance.")

    # DOUBLE CHECKED
    def get_markets_klines(self):
        """Gets data and validates the retrieved files
        Can raise Exception"""
        while True:
            try:
                # state-no:2.03 - get data
                self.logger.info("[state-no:2.03]")
                self.get_markets_klines_func()
                self.logger.debug("Passed state-no:2.03 - got data")

                # state-no:2.04 - validation check
                self.logger.info("[state-no:2.04]")
                bybit_csv_path = self.get_filepath("Temp/tData.csv")
                binance_csv_path = self.get_filepath("Temp/aData.csv")

                # Checking files individually
                (
                    is_binance_csv_checked,
                    is_binance_csv_volume_zero,
                    binance_info,
                ) = csv_kline_validator(binance_csv_path)
                (
                    is_bybit_csv_checked,
                    is_bybit_csv_volume_zero,
                    bybit_info,
                ) = csv_kline_validator(bybit_csv_path)

                if not is_binance_csv_checked:
                    self.logger.warning(
                        "Failed state-no:2.04 - " +
                        "Binance csv validity " +
                        f"check error {is_binance_csv_volume_zero}"
                    )
                    raise CustomException(
                        "Binance csv validation failed."
                    )
                else:
                    if is_binance_csv_volume_zero:
                        self.logger.warning(
                            "Binance csv contains kline(s) " +
                            f"with zero volume: \n{binance_info}"
                        )

                if not is_bybit_csv_checked:
                    self.logger.warning(
                        "Failed state-no:2.04 - " +
                        "Bybit csv validity " +
                        f"check error {is_bybit_csv_volume_zero}"
                    )
                    raise CustomException("Bybit csv validation failed.")
                else:
                    if is_bybit_csv_volume_zero:
                        self.logger.warning(
                            "Bybit csv contains kline(s) " +
                            f"with zero volume: \n{bybit_info}"
                        )

                # Check both files at once
                validity_check, error = validate_two_csvfiles(
                    binance_csv_path, bybit_csv_path
                )
                if validity_check:
                    self.logger.debug(
                        "Successfully checked Binance and Bybit csv " +
                        "files synchronization."
                    )
                else:
                    raise CustomException(
                        "Failed Binance and Bybit csv files " +
                        "synchronization check."
                    )

            except (RequestException, CustomException) as wrn:
                self.logger.warning(wrn)
                retry_after = self.GET_KLINE_RETRY_DELAY
                self.logger.debug(
                    "Retrying to get data after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.critical(ex)
                raise  # TERMINATES BOT
            else:
                self.logger.debug("Passed states-no:2.04.")
                return self.Result.SUCCESS

    # CHECKED
    def run_r_strategy(self):
        """Runs the RunStrategy.R code
        Returns nothing
        Raise Exception"""
        self.logger.info("[state-no:2.05]")
        r_filepath = NebBot.get_filepath("RunStrategy.R")
        is_passed = self.run_r_code(
            filepath=r_filepath,
            timeout=self.RUN_R_STRATEGY_TIMEOUT,
        )
        if not is_passed:
            # TERMINATES BOT
            raise Exception("Error running 'RunStrategy.R' code.")
        else:
            self.logger.debug("Passed state-no:2.05")
            # Validate R output signals
            self.logger.debug("[state-no:2.06]")
            self.validate_strategy_signals()
            self.logger.debug("Passed state-no:2.06")

    # CHECKED ???
    def validate_strategy_signals(self):
        """Validates strategy output signals
        Returns nothing
        Raises Exception"""
        l_en = self.get_r_strategy_output(enums.StrategyVariables.LongEntry)
        l_ex = self.get_r_strategy_output(enums.StrategyVariables.LongExit)
        s_en = self.get_r_strategy_output(enums.StrategyVariables.ShortEntry)
        s_ex = self.get_r_strategy_output(enums.StrategyVariables.ShortExit)
        psm = self.get_r_strategy_output(
            enums.StrategyVariables.PositionSizeMultiplier)

        # check the wrong signals
        if(
            ((l_en or s_en) and not (psm > 0)) or
            (l_en and s_en) or
            (l_ex and s_ex)
        ):
            # TERMINATES BOT
            raise Exception("Strategy signals are not valid.")
        else:
            self.logger.debug("Successful strategy signal validity check.")

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
                            f"Failed state no.{str(state_no).zfill(2)} " +
                            "- schedule timed out " +
                            f"(timeout ts:{retrieve_data_timeout_ts}," +
                            f" now:{timestamp_now()})"
                        )
                        return None

                    # state no.{state_no+1} - get data
                    self.logger.info(f"[state-no.{str(state_no+1).zfill(2)}]")
                    opd = retrieve_data_job.run_now()
                    self.logger.info(
                        f"Passed state no.{str(state_no+1).zfill(2)}" +
                        " - got open position data"
                    )

                    # state no.{state_no+2} - validation check
                    self.logger.info(f"[state-no.{str(state_no+2).zfill(2)}]")
                    if not str(opd["ret_code"]) == "0":
                        self.logger.info("validity check error.")
                        raise RequestException(
                            "Failed validity check - " +
                            "ret_code status is not 0."
                        )
                    self.logger.info(
                        f"Passed state no.{str(state_no+2).zfill(2)}" +
                        " - validity checked"
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
                        "Retrying to get data after " +
                        f"{retry_after} seconds."
                    )
                    time.sleep(retry_after)
                except Exception as ex:
                    self.logger.critical(ex)
                    raise Exception(ex)

                self.logger.debug("Retrying to see if job can run.")

    # CHECKED
    def redis_value_reset(self):
        """Reset the strategy out-put values in redis
        Returns nothing
        Raises no exception"""
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
        self.logger.debug("Strategy redis values reinitialized.")

    def get_orderbook_and_ltp(self):
        raise NotImplementedError


if __name__ == "__main__":
    bot = None
    try:
        # Change name and version of your bot:
        name = "Neb Bot"
        version = "0.4.08"

        # Do not delete these lines:
        bot = NebBot(name, version)
        bot.logger.debug("Successfully initialized bot")
        bot.logger.info("[state-no:1.01]")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
