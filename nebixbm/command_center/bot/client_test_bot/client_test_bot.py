import os

from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import BybitClient
from nebixbm.api_client.bybit.enums import Symbol, Coin


# Change name and version of your bot:
name = "client_test_bot"
version = "1.0.0"


class NebBot(BaseBot):
    """NebBot class"""

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

        # Get orderbook: (public endpoint - GET)
        symbol = Symbol.BTCUSD
        res = self.client.get_order_book(symbol=symbol)
        if res["ret_code"] == 0:
            self.logger.info("Successfully got the orderbook")
        else:
            self.logger.info("Failed to get the orderbook")
            self.logger.error(f"{res}")

        # Get account balance: (private - GET)
        coin = Coin.BTC
        res = self.client.get_wallet_balance(coin)
        if res["ret_code"] == 0:
            self.logger.info(
                f"Successfully got the account balance: {res['result']}"
            )
        else:
            self.logger.info("Failed to get account balance")
            self.logger.error(f"{res}")

        # Change leverage: (private - POST)
        new_levarage = 69
        symbol = Symbol.BTCUSD
        res = self.client.change_user_leverage(symbol, new_levarage)
        if res["ret_code"] == 0 and res["result"] == new_levarage:
            self.logger.info(
                f"Successfully changed leverage to {new_levarage} for {symbol}"
            )
        elif res["ret_code"] == 34015:
            self.logger.info(
                "No change in leverage - new leverage was the same as the"
                + " old leverage"
            )
        else:
            self.logger.info("Failed to change leverage")
            self.logger.error(f"{res}")

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:
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
