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
    BybitException,
)
from nebixbm.api_client.binance.client import (
    BinanceClient,
    BinanceException,
)
import nebixbm.api_client.bybit.enums as bybit_enum
import nebixbm.api_client.binance.enums as binance_enum
from nebixbm.command_center.bot.sample_bot import enums
from nebixbm.command_center.tools.scheduler import (
    c2s,
    timestamp_now,
    datetime_to_timestamp,
)
from nebixbm.command_center.tools.csv_validator import (
    csv_kline_validator,
    validate_two_csvfiles,
)
from nebixbm.command_center.tools.opd_validator import opd_validator
from nebixbm.command_center.tools.ob_validator import ob_validator
from nebixbm.command_center.tools.cp_validator import cp_validator
import json
import numpy as np


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

        self.GET_OPD_RETRY_DELAY = 5
        self.GET_OB_RETRY_DELAY = 5

        self.WAIT_CLOSE_LIQUIDITY = 5
        self.CLOSE_POSITION_DELAY = 5

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

        # initialize settings for strategy
        self.redis_reset_strategy_settings()

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
        opd = None
        if do_state == 3:
            self.redis_reset_strategy_output()
            self.get_markets_klines()
            self.run_r_strategy()
            opd = self.get_open_position_data(state_no=7)
            do_state = self.signal_evaluate(opd)
        if do_state == 12:
            self.close_position_section(state_no=do_state, opd=opd)

    # CHECKED ???
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
        Raises Exception"""
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

            except (RequestException, CustomException, BinanceException,
                    BybitException) as wrn:  # TODO Check it
                self.logger.info("[state-no:2.04]")
                self.logger.warning(wrn)
                retry_after = self.GET_KLINE_RETRY_DELAY
                self.logger.debug(
                    "Retrying to get data after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
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
            self.logger.info("[state-no:2.06]")
            self.validate_strategy_signals()
            self.logger.debug("Passed state-no:2.06")

    # DOUBLE CHECKED
    def validate_strategy_signals(self):
        """Validates strategy output signals
        Returns nothing
        Raises Exception"""
        l_en = self.redis_get_strategy_output(
            enums.StrategyVariables.LongEntry)
        l_ex = self.redis_get_strategy_output(
            enums.StrategyVariables.LongExit)
        s_en = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortEntry)
        s_ex = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortExit)
        psm = self.redis_get_strategy_output(
            enums.StrategyVariables.PositionSizeMultiplier)

        # check the wrong signals
        if not (((not l_en and l_ex and not s_ex) or
                 (not l_ex and not s_en and s_ex)) and psm > 0):
            # TERMINATES BOT
            raise Exception("Strategy signals are not valid.")
        else:
            self.logger.debug("Successful strategy signal validity check.")

    # CHECKED ???
    def get_open_position_data(self, state_no):
        """Gets open position data and validates the retrieved data
        Raises Exception"""
        while True:
            try:
                # state-no:2.07 or state-no:2.27 - get data
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
                symbol = self.BYBIT_SYMBOL
                opd = self.bybit_client.get_position(symbol)
                self.logger.debug(
                    f"Passed state-no:2.{str(state_no).zfill(2)} - got data"
                )

                # state-no:2.08 or state-no:2.28 - validation check
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                is_valid, error = opd_validator(opd)

                if not is_valid:
                    self.logger.warning(
                        f"Failed state-no:2.{str(state_no + 1).zfill(2)} - " +
                        "Open Position data validity " +
                        f"check error {error}"
                    )
                    raise CustomException(
                        "Open Position data validation failed."
                    )

            except (RequestException, CustomException,
                    BybitException) as wrn:  # TODO Check it
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.warning(wrn)
                retry_after = self.GET_OPD_RETRY_DELAY
                self.logger.debug(
                    "Retrying to get data after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                raise  # TERMINATES BOT
            else:
                self.logger.debug(
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}.")
                self.logger.debug("Open Position Data:\n" +
                                  f'Symbol:' +
                                  f'{opd["result"]["symbol"]}\n' +
                                  f'Side:' +
                                  f'{opd["result"]["side"]}\n' +
                                  f'Position value:' +
                                  f'{opd["result"]["position_value"]}\n' +
                                  f'Entry price:' +
                                  f'{opd["result"]["entry_price"]}\n' +
                                  f'Size:' +
                                  f'{opd["result"]["size"]}\n' +
                                  f'Leverage:' +
                                  f'{opd["result"]["leverage"]}\n' +
                                  f'Liq. price:' +
                                  f'{opd["result"]["liq_price"]}\n' +
                                  f'Stop loss:' +
                                  f'{opd["result"]["stop_loss"]}\n' +
                                  f'Deleverage indicator:' +
                                  f'{opd["result"]["deleverage_indicator"]}\n' +
                                  f'Created at:' +
                                  f'{opd["result"]["created_at"]}\n' +
                                  f'Updated at:' +
                                  f'{opd["result"]["updated_at"]}\n' +
                                  f'Time checked:' +
                                  f'{opd["time_now"]}')
                return opd["result"]

    # CHECKED
    def redis_reset_strategy_output(self):
        """Reset the strategy out-put values in redis
        Returns nothing
        Raises no exception"""
        self.redis.set(enums.StrategyVariables.EX_Done, "0")
        self.redis.set(enums.StrategyVariables.PP_Done, "0")
        self.redis.set(enums.StrategyVariables.StopLossValue, "NA")
        self.redis.set(enums.StrategyVariables.TimeCalculated, "NA")
        self.redis.set(enums.StrategyVariables.LongEntry, "FALSE")
        self.redis.set(enums.StrategyVariables.ShortEntry, "FALSE")
        self.redis.set(enums.StrategyVariables.LongExit, "FALSE")
        self.redis.set(enums.StrategyVariables.ShortExit, "FALSE")
        self.redis.set(enums.StrategyVariables.PositionSizeMultiplier, "0")
        self.redis.set(enums.StrategyVariables.Close, "NA")
        self.logger.debug("Strategy redis values reinitialized.")

    # DOUBLE CHECKED
    def redis_get_strategy_output(self, variable):
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
                or variable == enums.StrategyVariables.Close
        ):
            if value == "NA":
                return 0
                return 0
            if value == "0":
                return 0
            else:
                return float(value)
        else:
            raise Exception("Not a valid strategy value.")

    # CHECKED ???
    def redis_reset_strategy_settings(self):
        """Reset the strategy settings' values in redis
        Returns nothing
        Raises no exception"""
        self.redis.set(enums.StrategySettings.Liquidity_Slippage, 0.05)
        self.logger.debug("Strategy redis settings' values reinitialized.")

    # CHECKED ???
    def redis_get_strategy_settings(self, variable):
        """Converts Redis strategy settings' values to python readable values
        Returns the corresponding value in redis
        Raises Exception on non-strategy-setting-value requests"""
        value = self.redis.get(variable)
        if variable == enums.StrategySettings.Liquidity_Slippage:
            return float(value)
        else:
            raise Exception("Not a valid strategy settings' value.")

    # CHECKED
    def signal_evaluate(self, opd):
        """Evaluate signals
        Returns the next state to do
        Raises nothing"""
        l_en = self.redis_get_strategy_output(
            enums.StrategyVariables.LongEntry)
        l_ex = self.redis_get_strategy_output(
            enums.StrategyVariables.LongExit)
        s_en = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortEntry)
        s_ex = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortExit)

        self.logger.info("[state.no:2.09]")
        if l_ex or s_ex:
            self.logger.info("[state.no:2.10]")
            if not opd["side"] == bybit_enum.Side.NONE:
                self.logger.info("[state.no:2.11]")
                if ((opd["side"] == bybit_enum.Side.BUY and l_ex) or
                        (opd["side"] == bybit_enum.Side.SELL and s_ex)):
                    return 12
                else:
                    return 18
            else:
                return 18
        else:
            return 18

    # CHECKED
    def get_orderbook(self, state_no):
        """Gets orderbook data and validates the retrieved data
        Raises Exception
        Returns Orderbook list"""
        while True:
            try:
                # state-no:2.12 or state-no:2.21 - get data
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
                symbol = self.BYBIT_SYMBOL
                ob = self.bybit_client.get_order_book(symbol)
                self.logger.debug(
                    f"Passed state-no:2.{str(state_no).zfill(2)} - got data")

                # state-no:2.13 or state-no:2.22 - validation check
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                is_valid, error = ob_validator(ob)

                if not is_valid:
                    self.logger.warning(
                        f"Failed state-no:2.{str(state_no + 1).zfill(2)} - " +
                        "Orderbook data validity " +
                        f"check error {error}"
                    )
                    raise CustomException("Orderbook data validation failed.")

            except (RequestException, CustomException, BybitException) as wrn:
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.warning(wrn)
                retry_after = self.GET_OB_RETRY_DELAY
                self.logger.debug(
                    "Retrying to get data after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                raise  # TERMINATES BOT
            else:
                self.logger.debug(
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}.")
                # self.logger.debug("Orderbook:\n" +
                #                   f'{ob["result"]}')
                return ob

    # CHECKED ???
    def close_position_section(self, state_no, opd):
        is_adequate = False
        while not is_adequate:
            self.logger.debug("Closing the open position.")
            ob = self.get_orderbook(state_no)
            ls = self.redis_get_strategy_settings(
                enums.StrategySettings.Liquidity_Slippage)
            close = self.redis_get_strategy_output(
                enums.StrategyVariables.Close)
            bid_liq, ask_liq = self.calculate_liquidity(state_no + 2, ob, ls, close)
            is_adequate = self.evaluate_liquidity(
                state_no + 3,
                opd,
                bid_liq,
                ask_liq
            )
            if not is_adequate:
                # TODO: CHECK
                time.sleep(self.WAIT_CLOSE_LIQUIDITY)
            else:
                # pass to next schedule
                state_no = state_no + 4

        # close position state 16
        self.close_position(state_no, opd)

    # CHECKED ???
    def calculate_liquidity(self, state_no, ob, ls, close):
        """Calculates bid_liq and ask_liq and returns it"""
        self.logger.info(f"[state-no:2.{state_no}]")
        self.logger.info(f"Calculating liquidity.")
        # ob = json.loads(ob)["result"]
        ob = ob["result"]
        ar_ob = np.array([])
        for o in range(len(ob)):
            order = np.array([ob[o]["side"],
                              float(ob[o]["price"]),
                              float(ob[o]["size"])])
            ar_ob = np.append(ar_ob, order)

        ar_ob = ar_ob.reshape((len(ob), 3))

        index_buy = np.where(ar_ob[:, 0] == bybit_enum.Side.BUY)[0]
        best_bid = float(max(ar_ob[:, 1][index_buy]))

        index_sell = np.where(ar_ob[:, 0] == bybit_enum.Side.SELL)[0]
        best_ask = float(min(ar_ob[:, 1][index_sell]))

        ask_liq_bound = best_bid + ((ls / 100) * close)
        bid_liq_bound = best_ask - ((ls / 100) * close)

        # Calc. ask_liq
        price = ar_ob[:, 1].astype(np.float)
        c1 = np.greater_equal(price, best_ask)
        c2 = np.less_equal(price, ask_liq_bound)
        c3 = np.logical_and(c1, c2)
        sizes = ar_ob[:, 2][c3].astype(np.float)
        ask_liq = np.sum(sizes)

        # Calc. bid_liq
        price = ar_ob[:, 1].astype(np.float)
        c1 = np.less_equal(price, best_bid)
        c2 = np.greater_equal(price, bid_liq_bound)
        c3 = np.logical_and(c1, c2)
        sizes = ar_ob[:, 2][c3].astype(np.float)
        bid_liq = np.sum(sizes)
        # self.logger.debug(f"Orderbook as of:\nSide, Price, Size\n"
        #                   f"{str(ar_ob).replace('[', '').replace(']', '')}")
        self.logger.debug(f"Liquidity as of:\n" +
                          f"Best bid price: {best_bid} \n" +
                          f"Best ask price: {best_ask} \n" +
                          f"Ask liq. boundary: {ask_liq_bound} \n" +
                          f"Bid liq. boundary: {bid_liq_bound} \n" +
                          f"Ask liq.: {ask_liq} \n" +
                          f"Bid liq.: {bid_liq} \n")

        self.logger.debug(f"Successfully calculated liquidity slippage.")
        return bid_liq, ask_liq

    # CHECKED ???
    def evaluate_liquidity(self, state_no, opd, bid_liq, ask_liq):
        """Evaluates Liquidity by given inputs
        Returns True or False if it's adequate
        Raises no Exception"""
        self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
        self.logger.debug("Evaluating liquidity.")
        if opd["side"] == bybit_enum.Side.BUY:
            # The open position is Long
            if float(opd["size"]) < bid_liq:
                self.logger.debug("Adequate bid liquidity.")
                return True
            else:
                self.logger.warning("Inadequate bid liquidity.")
                return False
        elif opd["side"] == bybit_enum.Side.SELL:
            # The open position is Short
            if float(opd["size"]) < ask_liq:
                self.logger.debug("Adequate ask liquidity.")
                return True
            else:
                self.logger.warning("Inadequate ask liquidity.")
                return False

    # CHECKED ???
    def close_position(self, state_no, opd):
        """Close existing position using opd
        Returns nothing
        Raises RequestException and Exception"""
        self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
        while True:
            try:
                # state-no:2.16 or state-no:?.?? - get data
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")

                ot = bybit_enum.OrderType.MARKET
                qty = int(opd["size"])
                tif = bybit_enum.TimeInForce.IMMEDIATEORCANCEL
                ro = True
                side = bybit_enum.Side.NONE
                if opd["side"] == bybit_enum.Side.BUY:
                    side = bybit_enum.Side.SELL
                elif opd["side"] == bybit_enum.Side.SELL:
                    side = bybit_enum.Side.BUY

                self.logger.debug("Closing position:\n"
                                  f"Side: {side}\n" +
                                  f"Order type: {ot}\n" +
                                  f"Quantity: {qty}\n" +
                                  f"Time in force: {tif}\n" +
                                  f"Reduce only: {ro}\n")

                res = self.bybit_client.place_order(
                    side=side,
                    symbol=self.BYBIT_SYMBOL,
                    order_type=ot,
                    qty=qty,
                    time_in_force=tif,
                    reduce_only=ro,
                )

                self.logger.debug(
                    f"Passed state-no:2.{str(state_no).zfill(2)}")

                # state-no:2.17 or state-no:?.?? - validation check
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                is_valid, error = cp_validator(res)
                self.logger.debug("cp res\n" + res)  # TODO: remove

                if not is_valid:
                    self.logger.warning(
                        f"Failed state-no:2.{str(state_no + 1).zfill(2)} - " +
                        "Could not close position " +
                        f"error {error}"
                    )
                    raise CustomException("Close position validation failed.")

            except (RequestException, CustomException, BybitException) as wrn:  # TODO CHECK
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.warning(wrn)
                retry_after = self.CLOSE_POSITION_DELAY
                self.logger.debug(
                    "Retrying to close position after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                raise  # TERMINATES BOT
            else:
                self.logger.debug(
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}.")
                return



if __name__ == "__main__":
    bot = None
    try:
        # Change name and version of your bot:
        name = "Neb Bot"
        version = "0.4.21"

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
