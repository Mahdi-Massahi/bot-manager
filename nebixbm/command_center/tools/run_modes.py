import os

import nebixbm.api_client.bybit.enums as bybit_enum
import nebixbm.api_client.bitstamp.enums as bitstamp_enum
from nebixbm.database.driver import RedisDB


class Clients:
    """Implemented clients"""

    BYBIT = "Bybit"
    BITSTAMP = "Bitstamp"
    BINANCE = "Binance"


class Modes:
    """Enums for RunMode"""

    TNTS = "TNTS"           # Test Net Test Strategy
    MNTS = "MNTS-Warning"   # Main Net Test Strategy
    TNMS = "TNMS"           # Test Net Main Strategy
    MNMS = "MNMS"           # Main Net Main Strategy


class AlgoSettings:
    def __init__(self):
        self.interval = None


class TradingClientSettings:
    def __init__(
            self,
            client: Clients,
            limit: int,
            interval_m: int,
            security: str,
            is_on_testnet: bool,
    ):

        self.client = client
        self.interval = None
        self.security = None
        self.limit = limit

        if client == Clients.BYBIT:
            # Interval check
            if interval_m in bybit_enum.Interval.values():
                self.interval = interval_m
            else:
                raise Exception("Not a valid interval for Bybit client.")

            # Security check
            if security in bybit_enum.Symbol.value():
                self.security = security
            else:
                raise Exception("Not a valid security for Bybit client.")

            # API settings config
            if is_on_testnet:
                self.api_key = os.environ['BYBIT_TEST_APIKEY']
                self.secret = os.environ['BYBIT_TEST_SECRET']
            else:
                self.api_key = os.environ['BYBIT_MAIN_APIKEY']
                self.secret = os.environ['BYBIT_MAIN_SECRET']
        else:
            raise Exception("Not implemented client for trading.")


class AnalysisClintSettings:
    def __init__(
            self,
            client: Clients,
            limit: int,
            interval_m: int,
            security: str,):

        self.client = client
        self.security = None
        self.interval = None
        self.limit = limit

        if client == Clients.BITSTAMP:
            # Interval check
            interval_ss = str(interval_m * 60)
            if interval_ss in bitstamp_enum.Interval.values():
                self.interval = interval_ss
            else:
                raise Exception("Not implemented interval for Bitstamp.")

            # Security check
            if security in bitstamp_enum.Symbol.value():
                self.security = security
            else:
                raise Exception("Not a valid security for Bitstamp client.")

        else:
            raise Exception("Not implemented client for analysis.")


class RunMode:
    def __init__(
            self,
            name,
            mode: Modes,
            analysis_client: Clients,
            analysis_security,
            trading_client: Clients,
            trading_security,
            main_interval_m: int,
            test_interval_m: int,
            limit: int,
            do_notify_by_email: bool,
            do_notify_by_telegram: bool,
            do_validate_signals: bool,
    ):
        self.mode = mode
        self.test_interval_m = test_interval_m
        self.main_interval_m = main_interval_m
        self.do_notify_by_email = do_notify_by_email
        self.do_notify_by_telegram = do_notify_by_telegram
        self.do_validate_signals = do_validate_signals
        self.interval_m = 0
        self.is_on_testnet = None

        redis = RedisDB()

        # Strategy interval settings
        if mode == Modes.TNTS or mode == Modes.MNTS:
            self.interval_m = self.test_interval_m
            redis.set(name + ":[S]-Run-Test-Strategy", "TRUE")
        if mode == Modes.TNMS or mode == Modes.MNMS:
            self.interval_m = self.main_interval_m
            redis.set(name + ":[S]-Run-Test-Strategy", "FALSE")

        # Strategy API Settings
        if mode == Modes.MNMS or mode == Modes.MNTS:
            self.is_on_testnet = False
        if mode == Modes.TNMS or mode == Modes.TNTS:
            self.is_on_testnet = True

        self.trading_client_settings = TradingClientSettings(
            client=trading_client,
            limit=limit,
            interval_m=self.interval_m,
            security=trading_security,
            is_on_testnet=self.is_on_testnet,
        )

        self.analysis_client_settings = AnalysisClintSettings(
            client=analysis_client,
            limit=limit,
            interval_m=self.interval_m,
            security=analysis_security,
        )
