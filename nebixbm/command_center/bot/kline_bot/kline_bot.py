import os
import csv

from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import (
    BybitClient,
    timestamp_to_datetime,
)
from nebixbm.api_client.bybit.enums import Symbol, Interval


class NebBot(BaseBot):
    """NebBot class"""

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
            is_testnet=True, secret=secret, api_key=api_key, req_timeout=5
        )

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")

        symbol = Symbol.BTCUSD
        limit = 200
        interval = Interval.i5
        filepath = NebBot.get_filepath(
            f"kline_{symbol}_{interval}.csv"
        )
        self.get_kline_data(symbol, limit, interval, filepath)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        # Do not delete this line:
        super().before_termination()

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
        name = "kline_bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = NebBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
        bot.before_termination()
    except Exception as err:
        if bot is not None:
            bot.logger.exception(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
