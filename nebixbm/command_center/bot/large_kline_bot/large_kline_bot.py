import os
import csv
import time
import datetime

from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import (
    BybitClient,
    timestamp_to_datetime,
)
from nebixbm.api_client.bybit.enums import Symbol, Interval
from nebixbm.command_center.tools.scheduler import datetime_to_timestamp

# , c2s, timestamp_now,


class KlineBot(BaseBot):
    """KlineBot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        secret = os.environ['BYBIT_TEST_SECRET']
        api_key = os.environ['BYBIT_TEST_APIKEY']
        self.client = BybitClient(
            is_testnet=True, secret=secret, api_key=api_key, req_timeout=2
        )

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")

        symbol = Symbol.BTCUSD
        limit = 200
        interval = Interval.i240
        filepath = KlineBot.get_filepath(
            f"Large_Kline_{symbol}_{interval}.csv"
        )
        (
            next_kline_ts,
            last_kline_ts,
            delta,
        ) = self.client.get_kline_open_timestamps(symbol, interval)

        # end_ts = timestamp_now(mili=True) // 1000  # NOW
        # from_ts = int(end_ts - c2s(days=1))  # weeks=53 to get one year

        # 2019, 1, 2, 00, 01 -> 2020, 4, 1, 00, 00
        end_dt = datetime.datetime(2020, 4, 1, 00, 00)
        end_ts = datetime_to_timestamp(end_dt) // 1000
        from_datetime = datetime.datetime(2019, 1, 2, 00, 1)
        from_ts = datetime_to_timestamp(from_datetime) // 1000

        delta_ts = delta * limit
        self.got_first_data = False
        while from_ts <= end_ts:
            self.get_kline_data(symbol, from_ts, limit, interval, filepath)
            from_ts += delta_ts
            time.sleep(5)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        # Do not delete this line:
        super().before_termination()

    def get_kline_data(self, symbol, from_ts, limit, interval, filepath):
        """Get kline data"""
        if interval == Interval.Y:
            return

        from_dt = timestamp_to_datetime(from_ts)
        res = self.client.get_kline(symbol, interval, from_dt, limit)

        # if results exits in response:
        if not self.got_first_data:
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
                    self.last_index = count + 1

                with open(filepath, "w+", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(results)
                    self.logger.info("Successfully wrote results to file")

            else:
                self.logger.error(
                    "Something was wrong with API response. "
                    + f"The response was: {res}"
                )
            self.got_first_data = True

        else:
            if res and "result" in res and res["result"]:
                self.logger.info(
                    f"Writing kline csv results for symbol:{symbol}, "
                    + f"interval:{interval}..."
                )
                results = []
                for count, kline in enumerate(res["result"]):
                    results.append(
                        [
                            self.last_index + count + 1,
                            kline["open"],
                            kline["close"],
                            kline["high"],
                            kline["low"],
                            kline["volume"],
                            kline["open_time"],
                        ]
                    )
                self.last_index = self.last_index + count + 1

                with open(filepath, "a", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(results)
                    self.logger.info("Successfully wrote results to file")

            else:
                self.logger.error(
                    "Something was wrong with API response. "
                    + f"The response was: {res}"
                )

    @staticmethod
    def get_filepath(filename):
        """Get module-related filepath"""
        return os.path.join(os.path.dirname(__file__), filename)


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "large_kline_bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = KlineBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
        bot.before_termination()
    except Exception as err:
        if bot is not None:
            bot.logger.exception(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
