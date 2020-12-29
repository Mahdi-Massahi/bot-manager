import os
import time
import subprocess
import datetime
import numpy as np
from requests import RequestException
import psutil
import signal

from nebixbm.command_center.notification.email import EmailSender
from nebixbm.command_center.notification.telegram import TelegramClient
from nebixbm.database.driver import RedisDB
from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import (
    BybitClient,
    BybitException,
)
from nebixbm.api_client.bitstamp.client import (
    BitstampClient,
    BitstampException,
)
# from nebixbm.api_client.bitstamp.client import (
#     BitstampClient,
#     BitstampException,
# )
import nebixbm.api_client.bybit.enums as bybit_enum
import nebixbm.api_client.bitstamp.enums as bitstamp_enum
# import nebixbm.api_client.bitstamp.enums as bitstamp_enum
from nebixbm.command_center.bot.neb_bot import enums
from nebixbm.command_center.tools.scheduler import (
    c2s,
    timestamp_now,
    datetime_to_timestamp,
)
from nebixbm.command_center.tools.validator import (
    csv_kline_validator,
    two_csvfile_validator,
    opd_validator,
    ob_validator,
    cp_validator,
    op_validator,
    bl_validator,
    cl_validator,
    ct_validator,
)
from nebixbm.log.logger import (
    zip_existing_logfiles,
    delete_log_file,
)
import nebixbm.command_center.tools.Tracer as Tr

# Change name and version of your bot:
name = "neb_bot"
version = "3.0.3"

# save a list of running R subprocesses:
_r_subp_pid_list = []


class CustomException(Exception):
    pass


class NebBot(BaseBot):
    """Neb bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        secret = os.environ['BYBIT_TEST_SECRET']
        api_key = os.environ['BYBIT_TEST_APIKEY']
        # secret = os.environ['BYBIT_MAIN_SECRET']
        # api_key = os.environ['BYBIT_MAIN_APIKEY']
        self.bybit_client = BybitClient(
            is_testnet=True, secret=secret, api_key=api_key, req_timeout=5
        )
        self.bitstamp_client = BitstampClient(
            secret="", api_key="", req_timeout=5,
        )
        self.redis = RedisDB()
        self.tg_notify = TelegramClient(header=f"[({name}):{version}]")
        self.logger.debug("Notifier bot initialized.")
        self.LEVERAGE_CHANGE_TIMEOUT = 15

        email = os.getenv("NOTIFY_EMAIL")
        password = os.getenv("NOTIFY_PASS")
        smtp_host = os.getenv("EMAIL_SMTP_HOST")
        target = "notify.nebix@gmail.com"
        self.em_notify = EmailSender(
            sender_email=email,
            password=password,
            smtp_host=smtp_host,
            target_email=target,
            header=f"Message from [({name}):{version}] ",
        )
        e_text = "I have started to work now " \
                 "you can sleep because I'm awake :)"
        self.em_notify.send_email(subject=" - Bot starting",
                                  text=e_text)

        self.tracer = Tr.Tracer(name, version)

        self.T_ALGO_INTERVAL = 5 # 240  # in minutes
        self.SCHEDULE_DELTA_TIME = c2s(minutes=self.T_ALGO_INTERVAL) * 1000
        self.T_ALGO_TIMEOUT_DURATION = (
                c2s(minutes=self.T_ALGO_INTERVAL) * 0.90)

        # Kline properties
        self.BYBIT_COIN = bybit_enum.Coin.BTC
        self.BYBIT_SYMBOL = bybit_enum.Symbol.BTCUSD
        self.BYBIT_INTERVAL = bybit_enum.Interval.i5 # i240
        self.BYBIT_LIMIT = 200
        self.BITSTAMP_SYMBOL = bitstamp_enum.Symbol.BTCUSD
        self.BITSTAMP_INTERVAL = bitstamp_enum.Interval.i300# i14400
        self.BITSTAMP_LIMIT = 200

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.debug("Inside before_start()")

        # Run Install.R
        self.logger.info("[state-no:1.02]")
        self.logger.debug("Installing required packages for R.")
        file_path = NebBot.get_filepath("Install.R")
        state_installation_req = self.run_r_code(file_path, 60 * 30)

        # Install library
        lib_filepath = self.get_filepath("NebPackage/Neb_2.5.0.tar.gz")
        command = f"R CMD INSTALL --no-lock {lib_filepath}"
        state_installation_neb = self.run_cmd_command(command, 60 * 1)

        self.logger.info("[state-no:1.03]")
        self.logger.debug("Checking if packages are installed.")
        if state_installation_neb and state_installation_req:
            self.logger.debug("Required packages for R are installed.")
        else:
            self.logger.critical("Installing required packages for R failed.")
            raise Exception("Nothing can go forward!")

        # initialize settings for strategy
        self.logger.info("[state-no:1.04]")
        self.logger.debug("Resetting strategy setting values.")
        self.redis_reset_strategy_settings()

        # set the leverage
        try:
            res = self.run_with_timeout(
                self.set_leverage, None,
                self.LEVERAGE_CHANGE_TIMEOUT,
                self.Result.TIMED_OUT)
            if res == self.Result.FAIL:
                raise Exception("Failed to change the leverage.")
            if res == self.Result.TIMED_OUT:
                raise Exception("Timeouted to change the leverage.")
        except Exception as ex:
            raise Exception("Unhandled error during leverage changing: "
                            f"{ex}")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.debug("Inside start()")
        self.logger.info("[state-no:2.01]")

        # Bot starting datetime
        start_dt = datetime.datetime(2020, 12, 29, 17, 40, 0)
        start_ts = datetime_to_timestamp(start_dt, is_utc=True)

        # start_ts = timestamp_now() + 50

        # Bot termination datetime (end)
        end_dt = datetime.datetime(2021, 12, 30, 23, 59, 59)
        end_ts = datetime_to_timestamp(end_dt, is_utc=True)

        # first job timestamp (current job):
        job_start_ts = start_ts
        if job_start_ts < timestamp_now():
            raise Exception(
                "Job start timestamp already has passed.\n" +
                f"job start time: {job_start_ts}\n" +
                f"now\t\t{timestamp_now()}"
            )

        self.logger.debug(
            "Next job starts in "
            + f"{int(job_start_ts - timestamp_now())}ms"
        )
        # trading system schedule loop:
        run_trading_system = True
        while run_trading_system:
            if end_ts <= timestamp_now():
                self.logger.debug("Reached Bot end time.")
                e_text = f"The NEBIX [{name}:{version}]'s life has ended."
                self.em_notify.send_email(subject=" - Expiration",
                                          text=e_text)
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

                except Exception as ex:
                    self.logger.info("[state-no:3.01]")
                    self.logger.critical("Some exceptions stop trading-bot.")
                    self.logger.exception(ex)
                    self.tg_notify.send_message("%E2%9B%94 ***CRITICAL*** " +
                                                "\n" + str(ex))
                    self.before_termination()

            time.sleep(0.5)

    def trading_algo(self, do_state=3):
        """"TRADING ALGO.: returns only success or fail from result class"""
        opd = None
        ps = None
        tbl_usd = None
        pq_dev = None
        tbl = None
        if do_state == 3:
            self.redis_reset_strategy_output()
            self.get_markets_klines()
            self.run_r_strategy()
            opd = self.get_open_position_data(state_no=7)
            do_state = self.check_for_exit(opd)
        if do_state == 12:
            # Close position
            self.liquidity_analysis_for_closing(state_no=12, opd=opd)
            do_state = self.close_position(state_no=16, opd=opd)
        if do_state == 18:
            do_state = self.check_for_entry(state_no=18)
        if do_state == 19:
            # Open Position
            tbl = self.get_trading_balance(state_no=19)
            if tbl == 0:
                do_state = 34
            else:
                do_state = 22
        if do_state == 22:
            ps, tbl_usd = self.calculate_position_size(tbl)
            self.liquidity_analysis_for_opening(state_no=22, ps=ps)
            do_state = self.open_position(state_no=26, ps=ps)
        if do_state == 28:
            opd = self.get_open_position_data(state_no=28)
            if opd["side"] == bybit_enum.Side.NONE:
                self.logger.debug("Position has closed "
                                  "maybe by stop-loss.")
                do_state = 34
            else:
                do_state = 30
        if do_state == 30:
            pq_dev = self.calculate_pq_dev(state_no=30,
                                           opd=opd,
                                           tbl_usd=tbl_usd,
                                           ps=ps)
            do_state = self.is_deviated(state_no=31, pq_dev=pq_dev)
        if do_state == 32:
            # Modifying open position
            do_state = self.close_position(state_no=32,
                                           opd=opd,
                                           pq_dev=pq_dev)
        if do_state == 34:
            self.logger.info("[state-no:2.34]")
            self.logger.debug("Successfully ended schedule.")
            self.tg_notify.send_message("%E2%9C%94 "
                                        "Successfully ended schedule.")

    # CHECKED
    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.debug("Inside before_termination()")
        self.logger.info("[state-no:3.01]")

        # terminate alive R subprocesses:
        global _r_subp_pid_list
        self.logger.debug("Terminating R subprocesses...")
        for pid in _r_subp_pid_list:
            if psutil.pid_exists(pid):
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    self.logger.debug(f"Sent SIGTERM to pid={pid}")
                except Exception as er:
                    self.logger.error(
                        f"Failed to terminate R subprocess - Error: {er}"
                    )
        _r_subp_pid_list = []

        self.tg_notify.send_message("%E2%9B%94 Bot is terminating. ")
        time_now = str(datetime.datetime.utcnow())\
            .replace(":", "-").replace(" ", "-").replace(".", "-")
        text = f"NEBIX [{name}:{version}] is terminating du to some issues." \
               " Your attention is required.\n" \
               f"Date time: {time_now}\n"
        zip_path = None
        self.logger.debug("Compressing log files.")
        try:
            zip_path = zip_existing_logfiles()
            msg = "Log files are attached as needed."
            self.em_notify.send_email(subject=" - Bot termination",
                                      text=text+msg,
                                      filenames=[zip_path])
        except Exception as ex:
            self.logger.error("Failed to compress log files. error:", ex)
            msg = "There was an error compressing log files."
            self.em_notify.send_email(subject=" - Bot termination",
                                      text=text+msg)

        if not(zip_path is None):
            self.logger.debug("Deleting zipped log file.")
            try:
                delete_log_file(zip_path)
                self.logger.debug("Successfully deleted zipped file.")
            except Exception as ex:
                self.logger.error("Failed to delete the zipped file. " +
                                  f"error:{ex}")

        # Do not delete this line:
        super().before_termination()
        # TODO: https://stackoverflow.com/a/50381250  / name, format, from, to

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

        global _r_subp_pid_list

        # Remove the dead subprocesses from the list,
        # (prevents future overflow):
        for pid in _r_subp_pid_list:
            if not psutil.pid_exists(pid):
                _r_subp_pid_list.remove(pid)

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
                _r_subp_pid_list.append(proc.pid)
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
        """Get bybit and bitstamp kline data
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

        # Bitstamp data
        self.logger.debug("Getting Bitstamp data...")
        bitstamp_filepath = NebBot.get_filepath("Temp/aDataRaw.csv")
        bitstamp_data_success = self.bitstamp_client.kline_to_csv(
            symbol=self.BITSTAMP_SYMBOL,
            limit=self.BITSTAMP_LIMIT,
            interval=self.BITSTAMP_INTERVAL,
            filepath=bitstamp_filepath,
        )
        if not bitstamp_data_success:
            raise CustomException("Failed to get data from Bitstamp.")

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
                bitstamp_csv_path = self.get_filepath("Temp/aDataRaw.csv")

                # Checking files individually
                (
                    is_bitstamp_csv_checked,
                    is_bitstamp_csv_volume_zero,
                    bitstamp_info,
                ) = csv_kline_validator(bitstamp_csv_path)
                (
                    is_bybit_csv_checked,
                    is_bybit_csv_volume_zero,
                    bybit_info,
                ) = csv_kline_validator(bybit_csv_path)

                if not is_bitstamp_csv_checked:
                    self.logger.warning(
                        "Failed state-no:2.04 - " +
                        "Bitstamp csv validity " +
                        f"check error {is_bitstamp_csv_volume_zero}"
                    )
                    raise CustomException(
                        "Bitstamp csv validation failed."
                    )
                else:
                    if is_bitstamp_csv_volume_zero:
                        self.logger.warning(
                            "Bitstamp csv contains kline(s) " +
                            f"with zero volume: \n{bitstamp_info}"
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
                            "with zero volume."
                        )

                # Check both files at once
                validity_check, error = two_csvfile_validator(
                    bitstamp_csv_path, bybit_csv_path
                )
                if validity_check:
                    self.logger.debug(
                        "Successfully checked Bitstamp and Bybit csv " +
                        "files synchronization."
                    )
                else:
                    raise CustomException(
                        "Failed Bitstamp and Bybit csv files " +
                        f"synchronization check. error: {error}"
                    )

            except (RequestException, CustomException, BitstampException,
                    BybitException) as wrn:  # TODO Check it
                self.logger.info("[state-no:2.04]")
                self.logger.warning(wrn)
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.GetKlineRetryDelay)
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
        timeout = self.redis_get_strategy_settings(
            enums.StrategySettings.RunRStrategyTimeout)
        is_passed = self.run_r_code(
            filepath=r_filepath,
            timeout=timeout,
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
        slv = self.redis_get_strategy_output(
            enums.StrategyVariables.StopLossValue)
        close = self.redis_get_strategy_output(
            enums.StrategyVariables.Close)
        tcs = self.redis_get_strategy_output(
            enums.StrategyVariables.TimeCalculated)

        self.tracer.log(Tr.Trace.Signals,
                        [l_en, l_ex, s_en, s_ex, psm, slv, close, tcs])

        ls = l_en or s_en
        # check the wrong signals
        if not (
                (
                    # signals conflict check
                    (not l_en and not l_ex and not s_en and not s_ex) or
                    (not l_en and not l_ex and not s_en and s_ex) or
                    (not l_en and l_ex and not s_en and not s_ex) or
                    (not l_en and l_ex and s_en and not s_ex) or
                    (l_en and not l_ex and not s_en and s_ex)
                )
                and
                (
                    # making sure that psm exists when there is an entry
                    # signal
                    ((not l_en) and (not s_en) and (not psm > 0)) or
                    ((not l_en) and s_en and psm > 0) or
                    (l_en and (not s_en) and psm > 0)
                )
                and
                (
                    # making sure that stop-loss value is less than close for
                    # long positions
                    not (l_en and slv > close) or
                    # making sure that stop-loss value is greater than close
                    # for short positions
                    ((slv > close) or s_en) or
                    # making sure that stop-loss value exists when there is an
                    # entry signal
                    (not ls and slv == 0) or
                    (ls and slv != 0)
                )
        ):

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
                # state-no:2.07 or state-no:2.28 - get data
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
                symbol = self.BYBIT_SYMBOL
                opd = self.bybit_client.get_position(symbol)
                self.logger.debug(
                    f"Passed state-no:2.{str(state_no).zfill(2)} - got data"
                )

                # state-no:2.08 or state-no:2.29 - validation check
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
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.GetOPDRetryDelay)
                self.logger.debug(
                    "Retrying to get data after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                raise  # TERMINATES BOT
            else:
                dli = "deleverage_indicator"
                self.logger.debug(
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}.")
                self.logger.debug("Open position Data:\n" +
                                  'Symbol: ' +
                                  f'{opd["result"]["symbol"]}\n' +
                                  'Side: ' +
                                  f'{opd["result"]["side"]}\n' +
                                  'Position value: ' +
                                  f'{opd["result"]["position_value"]}\n' +
                                  'Entry price: ' +
                                  f'{opd["result"]["entry_price"]}\n' +
                                  'Size: ' +
                                  f'{opd["result"]["size"]}\n' +
                                  'Leverage: ' +
                                  f'{opd["result"]["leverage"]}\n' +
                                  'Liq. price: ' +
                                  f'{opd["result"]["liq_price"]}\n' +
                                  'Stop loss: ' +
                                  f'{opd["result"]["stop_loss"]}\n' +
                                  'Deleverage indicator: ' +
                                  f'{opd["result"][dli]}\n' +
                                  'Created at: ' +
                                  f'{opd["result"]["created_at"]}\n' +
                                  'Updated at: ' +
                                  f'{opd["result"]["updated_at"]}\n' +
                                  'Time checked: ' +
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
            else:
                return float(value)
        elif variable == enums.StrategyVariables.TimeCalculated:
            return value
        else:
            raise Exception("Not a valid strategy value.")

    # CHECKED
    def redis_reset_strategy_settings(self):
        """Reset the strategy settings' values in redis
        Returns nothing
        Raises no exception"""
        self.redis.set(enums.StrategySettings.Liquidity_Slippage, 0.05)
        self.redis.set(enums.StrategySettings.Withdraw_Amount, 0.0)
        self.redis.set(enums.StrategySettings.Withdraw_Apply, "FALSE")
        self.redis.set(enums.StrategySettings.GetKlineRetryDelay, 5)
        self.redis.set(enums.StrategySettings.RunRStrategyTimeout, 15)
        self.redis.set(enums.StrategySettings.GetOPDRetryDelay, 2)
        self.redis.set(enums.StrategySettings.GetOBRetryDelay, 2)
        self.redis.set(enums.StrategySettings.WaitCloseLiquidity, 1)
        self.redis.set(enums.StrategySettings.ClosePositionDelay, 2)
        self.redis.set(enums.StrategySettings.GetBLRetryDelay, 1)
        self.redis.set(enums.StrategySettings.WaitOpenLiquidity, 1)
        self.redis.set(enums.StrategySettings.OpenPositionDelay, 2)
        self.redis.set(enums.StrategySettings.ChangeLeverageDelay, 2)
        self.redis.set(enums.StrategySettings.MinimumTradingBalance, 0.003)
        self.redis.set(enums.StrategySettings.ChangeTriggerPriceDelay, 1)
        self.redis.set(enums.StrategySettings.ChangeTriggerPriceRetries, 10)
        self.logger.debug("Strategy redis settings' values reinitialized.")

    # CHECKED ???
    def redis_get_strategy_settings(self, variable):
        """Converts Redis strategy settings' values to python readable values
        Returns the corresponding value in redis
        Raises Exception on non-strategy-setting-value requests"""
        value = self.redis.get(variable)
        if (variable == enums.StrategySettings.Liquidity_Slippage or
                variable == enums.StrategySettings.Withdraw_Amount or
                variable == enums.StrategySettings.BybitTakerFee or
                variable == enums.StrategySettings.RMRule or
                variable == enums.StrategySettings.GetKlineRetryDelay or
                variable == enums.StrategySettings.RunRStrategyTimeout or
                variable == enums.StrategySettings.GetOPDRetryDelay or
                variable == enums.StrategySettings.GetOBRetryDelay or
                variable == enums.StrategySettings.WaitCloseLiquidity or
                variable == enums.StrategySettings.ClosePositionDelay or
                variable == enums.StrategySettings.GetBLRetryDelay or
                variable == enums.StrategySettings.WaitOpenLiquidity or
                variable == enums.StrategySettings.OpenPositionDelay or
                variable == enums.StrategySettings.ChangeLeverageDelay or
                variable == enums.StrategySettings.MinimumTradingBalance or
                variable == enums.StrategySettings.ChangeTriggerPriceDelay or
                variable == enums.StrategySettings.ChangeTriggerPriceRetries):
            return float(value)
        elif variable == enums.StrategySettings.Withdraw_Apply:
            if value == "TRUE":
                return True
            else:
                return False
        else:
            raise Exception("Not a valid strategy settings' value.")

    # CHECKED
    def check_for_exit(self, opd):
        """Evaluate signals
        Returns the next state to do
        Raises nothing"""
        l_ex = self.redis_get_strategy_output(
            enums.StrategyVariables.LongExit)
        s_ex = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortExit)

        self.logger.info("[state-no:2.09]")
        if l_ex or s_ex:
            self.logger.debug("Exit signal on strategy output.")
            self.logger.info("[state-no:2.10]")
            if not opd["side"] == bybit_enum.Side.NONE:
                self.logger.debug("There is an open position.")
                self.logger.info("[state-no:2.11]")
                if ((opd["side"] == bybit_enum.Side.BUY and l_ex) or
                        (opd["side"] == bybit_enum.Side.SELL and s_ex)):
                    self.logger.debug("Same side on open position " +
                                      "and strategy exit signal.")
                    return 12
                else:
                    self.logger.debug("Not same side on open position " +
                                      "and strategy exit signal.")
                    return 34
            else:
                self.logger.debug("There is no open position.")
                return 18
        else:
            self.logger.debug("No exit signal on strategy output.")
            return 18

    # CHECKED
    def get_orderbook(self, state_no):
        """Gets orderbook data and validates the retrieved data
        Raises Exception
        Returns Orderbook list"""
        while True:
            try:
                # state-no:2.12 or state-no:2.22 - get data
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
                symbol = self.BYBIT_SYMBOL
                ob = self.bybit_client.get_order_book(symbol)
                self.logger.debug(
                    f"Passed state-no:2.{str(state_no).zfill(2)} - got data")

                # state-no:2.13 or state-no:2.23 - validation check
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
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.GetBLRetryDelay)
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
                return ob

    # CHECKED
    def liquidity_analysis_for_closing(self, state_no, opd):
        is_adequate = False
        while not is_adequate:
            ob = self.get_orderbook(state_no)
            ls = self.redis_get_strategy_settings(
                enums.StrategySettings.Liquidity_Slippage)
            close = self.redis_get_strategy_output(
                enums.StrategyVariables.Close)
            bid_liq, ask_liq = self.calculate_liquidity(
                state_no + 2, ob, ls, close)
            is_adequate = self.evaluate_liquidity_for_closing(
                state_no + 3,
                opd,
                bid_liq,
                ask_liq
            )
            if not is_adequate:
                time.sleep(self.redis_get_strategy_settings(
                    enums.StrategySettings.WaitCloseLiquidity))

    # CHECKED ???
    def calculate_liquidity(self, state_no, ob, ls, close):
        """Calculates bid_liq and ask_liq and returns it"""
        self.logger.info(f"[state-no:2.{state_no}]")
        self.logger.debug("Calculating liquidity.")
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
        self.logger.debug("Liquidity as of:\n" +
                          f"Best bid price: {best_bid} \n" +
                          f"Best ask price: {best_ask} \n" +
                          f"Ask liq. boundary: {ask_liq_bound} \n" +
                          f"Bid liq. boundary: {bid_liq_bound} \n" +
                          f"Ask liq.: {ask_liq} \n" +
                          f"Bid liq.: {bid_liq}")

        self.logger.debug("Successfully calculated liquidity slippage.")
        return bid_liq, ask_liq

    # CHECKED ???
    def evaluate_liquidity_for_closing(self, state_no, opd, bid_liq, ask_liq):
        """Evaluates Liquidity by given inputs
        Returns True or False if it's adequate
        Raises Exception"""
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
        else:
            raise Exception("NO POSITION")

    # CHECKED ???
    def close_position(self, state_no, opd, pq_dev=None):
        """Closes existing position using opd or
        modifies it using pq_dev and opd
        Returns nothing
        Raises RequestException and Exception"""
        action = "Close"
        while True:
            try:
                # state-no:2.16 or state-no:2.32 - close position
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")

                if pq_dev is not None:
                    action = "Modify"

                ot = bybit_enum.OrderType.MARKET
                tif = bybit_enum.TimeInForce.IMMEDIATEORCANCEL
                ro = True
                side = bybit_enum.Side.NONE
                if opd["side"] == bybit_enum.Side.BUY:
                    side = bybit_enum.Side.SELL
                elif opd["side"] == bybit_enum.Side.SELL:
                    side = bybit_enum.Side.BUY
                qty = int(opd["size"])
                if action == "Modify":
                    qty = pq_dev

                self.logger.debug(f"{action}ing position:\n"
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

                if not is_valid:
                    self.logger.warning(
                        f"Failed state-no:2.{str(state_no + 1).zfill(2)} - " +
                        f"Could not {action.lower()} position " +
                        f"error {error}"
                    )
                    raise CustomException(
                        f"{action} position validation failed.")

            except (RequestException, CustomException, BybitException) as wrn:
                # TODO CHECK
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.exception(wrn)
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.ClosePositionDelay)
                self.logger.debug(
                    f"Retrying to {action.lower()} position after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                raise  # TERMINATES BOT
            else:
                if str(res["ret_code"]) == "0":
                    self.logger.debug(f"{action} position data:\n" +
                                      'Order ID: ' +
                                      f'{res["result"]["order_id"]}\n' +
                                      'Side: ' +
                                      f'{res["result"]["side"]}\n' +
                                      'Price: ' +
                                      f'{res["result"]["price"]}\n' +
                                      'Quantity: ' +
                                      f'{res["result"]["qty"]}\n' +
                                      'Time in force: ' +
                                      f'{res["result"]["time_in_force"]}\n' +
                                      'Order status: ' +
                                      f'{res["result"]["order_status"]}\n' +
                                      'Leaves quantity: ' +
                                      f'{res["result"]["leaves_qty"]}\n' +
                                      'Created at: ' +
                                      f'{res["result"]["created_at"]}\n' +
                                      'Updated at: ' +
                                      f'{res["result"]["updated_at"]}\n' +
                                      'Time: ' +
                                      f'{res["time_now"]}')

                    self.tracer.log(Tr.Trace.Trades,
                                    [
                                        action,
                                        res["result"]["side"],
                                        res["result"]["price"],
                                        res["result"]["qty"],
                                        "NA",
                                        res["result"]["leaves_qty"],
                                        ro,
                                        res["result"]["time_in_force"],
                                        res["result"]["order_status"],
                                        res["result"]["order_id"],
                                        res["result"]["created_at"],
                                        res["result"]["updated_at"],
                                        res["time_now"],
                                    ])

                elif str(res["ret_code"]) == "30063":
                    self.logger.debug(f"{action} position data:\n" +
                                      "Position is already closed. " +
                                      "(maybe by stop-loss)\n" +
                                      'Time: ' +
                                      f'{res["time_now"]}')
                self.logger.debug(
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}.")
                return state_no + 2

    # CHECKED ???
    def check_for_entry(self, state_no):
        """Checks for any entry signal
        Returns state_no
        Raises ???"""
        self.logger.debug("Checking for any entry signal.")
        self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
        l_en = self.redis_get_strategy_output(
            enums.StrategyVariables.LongEntry)
        s_en = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortEntry)

        if not (l_en or s_en):
            self.logger.debug("No entry signal.")
            return 34
        else:
            if l_en:
                self.logger.debug("Long entry signal received.")
                return 19
            self.logger.debug("Short entry signal received.")
            return 19

    # CHECKED ???
    def get_trading_balance(self, state_no):
        """Gets balance and applies withdraw amount
        Returns tbl (Trading Balance)
        Raises RequestException and Exception"""
        bl = self.get_balance(state_no)

        self.logger.info(f"[state-no:2.{state_no + 2}]")
        self.logger.debug("Calculating balance.")
        balance = float(bl["result"][self.BYBIT_COIN]["equity"])
        trading_balance = balance

        withdraw_amount = self.redis_get_strategy_settings(
            enums.StrategySettings.Withdraw_Amount)
        withdraw_apply = self.redis_get_strategy_settings(
            enums.StrategySettings.Withdraw_Apply)

        if withdraw_apply:
            self.logger.debug("Withdraw flag is True.")
            if 0 < withdraw_amount < balance:
                trading_balance = balance - withdraw_amount
                self.logger.debug("Withdraw amount is applied.")
                text = "Withdraw amount is applied.\n" + \
                       f"Withdrawal of {withdraw_amount}" + \
                       "BTC minus withdrawal fee is allowed.\n" + \
                       "Current trading balance is " + \
                       f"{trading_balance}BTC"
            else:
                text = "Invalid withdrawal amount.\n " \
                       "Withdraw flag reset to FALSE. \n" \
                       f"Current trading balance is {trading_balance}BTC"
                self.logger.error("Invalid withdraw amount.")
                self.redis.set(enums.StrategySettings.Withdraw_Apply, "FALSE")

            self.tg_notify.send_message("%E2%9A%A0 " + text)
            self.em_notify.send_email(
                subject=" - withdrawal notification",
                text=text)

        self.logger.debug("Balance info:\n" +
                          "Equity: " +
                          f"{balance}\n" +
                          "Withdraw amount: " +
                          f"{withdraw_amount}\n" +
                          "Trading balance: " +
                          f"{trading_balance}\n" +
                          'Realized PNL: ' +
                          f'{bl["result"]["BTC"]["realised_pnl"]}\n' +
                          'Time checked: ' +
                          f'{bl["time_now"]}')

        min_trading_balance = self.redis_get_strategy_settings(
            enums.StrategySettings.MinimumTradingBalance
        )

        if trading_balance < min_trading_balance:
            self.logger.debug("Trading balance is less than specified value.")
            text = "Trading balance is less than specified value " + \
                   f"which is {min_trading_balance} BTC."
            self.tg_notify.send_message("%E2%9A%A0 " + text)
            self.em_notify.send_email(
                subject=" - balance notification",
                text=text)
            return 0

        return trading_balance

    # CHECKED ???
    def get_balance(self, state_no):
        """Gets balance
        Raises RequestException and Exception
        Returns balance"""
        while True:
            try:
                # state-no:2.19 or state-no:2.?? - get balance
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
                self.logger.debug("Getting balance information.")
                coin = self.BYBIT_COIN
                bl = self.bybit_client.get_wallet_balance(coin)
                self.logger.debug(
                    f"Passed states-no:2.{str(state_no).zfill(2)}." +
                    " - got data")

                # state-no:2.20 or state-no:2.?? - validation check
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.debug("Validating balance information.")
                is_valid, error = bl_validator(bl)

                if not is_valid:
                    self.logger.warning(
                        f"Failed state-no:2.{str(state_no + 1).zfill(2)} - " +
                        "Balance data validity " +
                        f"check error {error}"
                    )
                    raise CustomException("Balance data validation failed.")

            except (RequestException, CustomException, BybitException) as wrn:
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.warning(wrn)
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.GetBLRetryDelay)
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
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}." +
                    " - data validated")
                return bl

    # CHECKED
    def liquidity_analysis_for_opening(self, state_no, ps):
        is_adequate = False
        while not is_adequate:
            ob = self.get_orderbook(state_no)
            ls = self.redis_get_strategy_settings(
                enums.StrategySettings.Liquidity_Slippage)
            close = self.redis_get_strategy_output(
                enums.StrategyVariables.Close)
            bid_liq, ask_liq = self.calculate_liquidity(state_no + 2,
                                                        ob, ls, close)
            is_adequate = self.evaluate_liquidity_for_opening(
                state_no + 3,
                ps,
                bid_liq,
                ask_liq,
            )
            if not is_adequate:
                time.sleep(self.redis_get_strategy_settings(
                    enums.StrategySettings.WaitOpenLiquidity))

    # CHECKED ???
    def evaluate_liquidity_for_opening(self, state_no, ps, bid_liq, ask_liq):
        """Evaluates Liquidity by given inputs
        Returns True or False if it's adequate
        Raises Exception"""
        self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
        self.logger.debug("Evaluating liquidity.")

        l_en = self.redis_get_strategy_output(
            enums.StrategyVariables.LongEntry)
        s_en = self.redis_get_strategy_output(
            enums.StrategyVariables.ShortEntry)

        if l_en:
            # The signal is Long
            if ps < ask_liq:
                self.logger.debug("Adequate ask liquidity.")
                return True
            else:
                self.logger.warning("Inadequate ask liquidity.")
                return False
        elif s_en:
            # The signal is Short
            if ps < bid_liq:
                self.logger.debug("Adequate bid liquidity.")
                return True
            else:
                self.logger.warning("Inadequate bid liquidity.")
                return False

    # CHECKED ???
    def calculate_position_size(self, tbl):
        """Calculates position size using 'tbl', 'psm' and 'close'
        Returns position size and tbl_usd"""
        psm = self.redis_get_strategy_output(
            enums.StrategyVariables.PositionSizeMultiplier)
        close = self.redis_get_strategy_output(
            enums.StrategyVariables.Close)

        tbl_usd = close * tbl
        position_size = int(psm * tbl_usd)

        if position_size == 0:
            position_size = 1
            self.logger.warning("Position size was bellow 1USD. "
                                "Opening position with 1$.")

        self.logger.debug(f"Balance is {round(tbl_usd, 2)} USD.")
        self.logger.debug(f"Position size is {position_size} USD.")

        return position_size, tbl_usd

    # CHECKED ???
    def open_position(self, state_no, ps):
        """Open a new position using 'ps'
        Returns next state no
        Raises RequestException and Exception"""
        slv = None
        while True:
            try:
                # state-no:2.26 or state-no:?.?? - open position
                self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")

                l_en = self.redis_get_strategy_output(
                    enums.StrategyVariables.LongEntry)
                s_en = self.redis_get_strategy_output(
                    enums.StrategyVariables.ShortEntry)
                slv = self.redis_get_strategy_output(
                    enums.StrategyVariables.StopLossValue)

                slv = round(slv * 2) / 2
                ot = bybit_enum.OrderType.MARKET
                qty = ps
                tif = bybit_enum.TimeInForce.IMMEDIATEORCANCEL
                ro = False
                side = bybit_enum.Side.NONE
                if l_en:
                    side = bybit_enum.Side.BUY
                elif s_en:
                    side = bybit_enum.Side.SELL

                self.logger.debug("Opening position:\n"
                                  f"Side: {side}\n" +
                                  f"Order type: {ot}\n" +
                                  f"Quantity: {qty}\n" +
                                  f"Stop-loss: {slv}\n" +
                                  f"Time in force: {tif}\n" +
                                  f"Reduce only: {ro}")

                res = self.bybit_client.place_order(
                    side=side,
                    symbol=self.BYBIT_SYMBOL,
                    order_type=ot,
                    qty=qty,
                    time_in_force=tif,
                    reduce_only=ro,
                    stop_loss=slv,
                )
                self.logger.debug(
                    f"Passed state-no:2.{str(state_no).zfill(2)}")

                # state-no:2.27  or state-no:?.?? - validation check
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                is_valid, error = op_validator(res)

                if is_valid and str(res["ret_code"]) == "30028":
                    self.logger.warning("Failed to open position. "
                                        "Market price has moved beyond "
                                        "stop-loss before opening position.")
                    return 34

                if not is_valid:
                    self.logger.warning(
                        f"Failed state-no:2.{str(state_no + 1).zfill(2)} - " +
                        "Could not open position " +
                        f"error {error}"
                    )
                    raise CustomException("Open position validation failed.")

            except (RequestException, CustomException,
                    BybitException) as wrn:  # TODO CHECK
                self.logger.info(f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                self.logger.exception(wrn)
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.OpenPositionDelay)
                self.logger.debug(
                    "Retrying to open position after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                raise  # TERMINATES BOT
            else:
                # Open position data is validated
                # Changing the trigger price for stop-loss
                retry_num = self.redis_get_strategy_settings(
                    enums.StrategySettings.ChangeTriggerPriceRetries)
                ct_is_valid = False
                sl_trigger_by = "Last"

                for retry in range(0, retry_num):
                    try:
                        self.logger.debug("Changing stop-loss trigger price.")
                        res_ct = self.bybit_client.change_stoploss_trigger_by(
                            sl_trigger_by=bybit_enum.TriggerBy.MARKPRICE,
                            symbol=bybit_enum.Symbol.BTCUSD,
                            stop_loss=slv
                        )
                        ct_is_valid, error = ct_validator(res_ct)
                        if ct_is_valid:
                            self.logger.debug("Successfully changed stop-loss"
                                              " trigger price.")
                            sl_trigger_by = \
                                res_ct["result"]["ext_fields"]["sl_trigger_by"]
                            break

                    except (RequestException, CustomException,
                            BybitException) as wrn:  # TODO CHECK
                        # self.logger.info(
                        #     f"[state-no:2.{str(state_no + 1).zfill(2)}]")
                        self.logger.exception(wrn)
                        retry_after = self.redis_get_strategy_settings(
                            enums.StrategySettings.ChangeTriggerPriceDelay)
                        self.logger.debug(
                            "Retrying to change trigger price after " +
                            f"{retry_after} seconds."
                        )
                        time.sleep(retry_after)

                self.logger.debug("Open position data:\n" +
                                  'Order ID: ' +
                                  f'{res["result"]["order_id"]}\n' +
                                  'Side: ' +
                                  f'{res["result"]["side"]}\n' +
                                  'Price: ' +
                                  f'{res["result"]["price"]}\n' +
                                  'Quantity: ' +
                                  f'{res["result"]["qty"]}\n' +
                                  'Time in force: ' +
                                  f'{res["result"]["time_in_force"]}\n' +
                                  'Order status: ' +
                                  f'{res["result"]["order_status"]}\n' +
                                  'Leaves quantity: ' +
                                  f'{res["result"]["leaves_qty"]}\n' +
                                  'Created at: ' +
                                  f'{res["result"]["created_at"]}\n' +
                                  'Updated at: ' +
                                  f'{res["result"]["updated_at"]}\n' +
                                  'Time: ' +
                                  f'{res["time_now"]}')

                self.tracer.log(Tr.Trace.Trades,
                                [
                                    "Open",
                                    res["result"]["side"],
                                    res["result"]["price"],
                                    res["result"]["qty"],
                                    slv,
                                    sl_trigger_by,
                                    res["result"]["leaves_qty"],
                                    ro,
                                    res["result"]["time_in_force"],
                                    res["result"]["order_status"],
                                    res["result"]["order_id"],
                                    res["result"]["created_at"],
                                    res["result"]["updated_at"],
                                    res["time_now"],
                                ])

                self.logger.debug(
                    f"Passed states-no:2.{str(state_no + 1).zfill(2)}.")
                return state_no + 2

    # CHECKED ???
    def calculate_pq_dev(self, state_no, opd, tbl_usd, ps):
        """Calculates Position Quantity Deviation and returns it"""
        self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
        self.logger.debug("Calculating position modification values.")
        close = self.redis_get_strategy_output(
            enums.StrategyVariables.Close)
        fee = self.redis_get_strategy_settings(
            enums.StrategySettings.BybitTakerFee)
        ep = float(opd["entry_price"])
        rmrule = self.redis_get_strategy_settings(
            enums.StrategySettings.RMRule)
        slv = self.redis_get_strategy_output(
            enums.StrategyVariables.StopLossValue)
        psm = (rmrule-2*fee)/((100*abs(ep-slv))/close)
        pq_dev = round(ps - (psm*tbl_usd))
        self.logger.debug("Modification info:\n" +
                          f"Position size multiplier: {psm}\n" +
                          f"Position quantity deviation: {pq_dev} USD\n" +
                          f"Entry to close deviation: {ep-close}")
        return pq_dev

    # CHECKED ???
    def is_deviated(self, state_no, pq_dev):
        """Checking if position needs to be modified."""
        self.logger.info(f"[state-no:2.{str(state_no).zfill(2)}]")
        self.logger.debug("Checking if position needs to be modified.")

        if pq_dev <= 0:  # TODO ERROR
            self.logger.debug("No modification needed.")
            return 34
        else:
            self.logger.debug("Modification needed.")
            return 32

    # CHECKED ???
    def set_leverage(self, leverage=0):
        """Set leverage and validates the retrieved data
        Raises Exception
        Returns RESULT"""
        while True:
            try:
                # state-no:1.05 - get data
                self.logger.info("[state-no:1.05]")
                self.logger.debug("Changing account leverage.")
                symbol = self.BYBIT_SYMBOL
                cl = self.bybit_client.change_user_leverage(symbol, leverage)

                # state-no:1.06 - validation check
                self.logger.info("[state-no:1.06]")
                is_valid, error = cl_validator(cl)

                if not is_valid:
                    self.logger.warning(
                        "Failed state-no:1.06 - " +
                        "Change leverage data validity " +
                        f"check error {error}"
                    )
                    raise CustomException("Change leverage data "
                                          "validation failed.")

            except (RequestException, CustomException, BybitException) as wrn:
                self.logger.info("[state-no:1.06]")
                self.logger.warning(wrn)
                retry_after = self.redis_get_strategy_settings(
                    enums.StrategySettings.ChangeLeverageDelay)
                self.logger.debug(
                    "Retrying to set data after " +
                    f"{retry_after} seconds."
                )
                time.sleep(retry_after)
            except Exception as ex:
                self.logger.error(ex)
                return self.Result.FAIL
            else:
                self.logger.debug("Passed states-no:1.06.")
                return self.Result.SUCCESS


if __name__ == "__main__":
    bot = None
    try:
        # Do not delete these lines:
        bot = NebBot(name, version)
        bot.logger.debug("Successfully initialized bot.")
        bot.logger.info("[state-no:1.01]")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot:
            bot.logger.critical(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
        raise
