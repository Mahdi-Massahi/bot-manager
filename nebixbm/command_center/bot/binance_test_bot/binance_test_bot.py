import csv
import os

from nebixbm.api_client.binance.client import BinanceClient
from nebixbm.api_client.binance.enums import Symbol, Interval
from nebixbm.command_center.bot.base_bot import BaseBot


class BinanceBot(BaseBot):
    """Binance test bot class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)

    def before_start(self):
        """Bot Manager calls this before running the bot"""
        self.logger.info("inside before_start()")
        # TODO: DELETE
        secret = (
            "T7HPbvgxdzbEvJrd5iCquFUBrcO5lGr"
            "sOqModH0HoW2ExbM9I67zzw1N4UsK8Fi5"
        )
        api_key = (
            "9XxTijoinAzafcrHqiBGyhYtVi6V8"
            "0qQvlZDKcTaRry2fd5GfcwBFYMyP5LJVxUM"
        )
        self.client = BinanceClient(
            secret=secret, api_key=api_key, req_timeout=5,
        )

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")

        symbol = Symbol.BTCUSDT
        interval = Interval.i5m
        klines = self.client.get_kline(symbol, interval, limit=200)
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
                results.append([c + 1, k[1], k[4], k[2], k[3], k[5], k[0]])

            with open(
                BinanceBot.get_filepath("klines.csv"), "w+", newline=""
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(results)
                self.logger.info("Successfully wrote results to file")

        else:
            self.logger.error(
                "Something was wrong with API response. "
                + f"The response was: {klines}"
            )

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        # Do not delete this line:
        super().before_termination()

    @staticmethod
    def get_filepath(filename):
        """Get module-related filepath"""
        return os.path.join(os.path.dirname(__file__), filename)


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Binance Test Bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = BinanceBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
