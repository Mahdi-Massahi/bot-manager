from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.api_client.bybit.client import BybitClient
from nebixbm.api_client.bybit.enums import (
    Symbol,
    Side,
    TimeInForce,
    OrderType,
)


class OrderBot(BaseBot):
    """Order bot class"""

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
            is_testnet=True, secret=secret, api_key=api_key, req_timeout=5,
        )

    def start(self):
        """This method is called when algorithm is run"""
        self.logger.info("inside start()")

        side = Side.SELL
        symbol = Symbol.BTCUSD
        order_type = OrderType.MARKET
        qty = 2
        time_in_force = TimeInForce.GOODTILLCANCEL
        res = self.client.place_order(
            side, symbol, order_type, qty, time_in_force
        )

        print(res)

    def before_termination(self, *args, **kwargs):
        """Bot Manager calls this before terminating a running bot"""
        self.logger.info("inside before_termination()")
        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:

        # Change name and version of your bot:
        name = "Order Bot"
        version = "1.0.0"

        # Do not delete these lines:
        bot = OrderBot(name, version)
        bot.logger.info("Successfully initialized bot")
        bot.before_start()
        bot.start()
    except Exception as err:
        if bot is not None:
            bot.logger.error(err)
            if not bot.has_called_before_termination:
                bot.before_termination()
