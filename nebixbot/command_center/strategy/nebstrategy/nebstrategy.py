from nebixbot.command_center.strategy.base_strategy import BaseStrategy
from nebixbot.api_client.bybit.client import BybitClient
from nebixbot.api_client.bybit.enums import Symbol, Coin


class NebStrategy(BaseStrategy):
    """This is NebStrategy class"""

    def __init__(self, name, version):
        """Init with name and version"""
        # Do not delete this line:
        super().__init__(name, version)
        #
        # Add your code here
        #

    def before_start(self):
        """Strategy Manager calls this before running the strategy"""
        self.logger.info("inside before_start()")
        secret = "0Quv1noKsVw3PbUGDTDERbMJEIxDk7AVXql3"  # TODO: DELETE
        api_key = "jL7iGHOqFUfWcGBcH5"  # TODO: DELETE
        self.client = BybitClient(
            is_testnet=True, secret=secret, api_key=api_key, req_timeout=2
        )

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

        # Get account balance: (private - GET)
        coin = Coin.BTC
        res = self.client.get_wallet_balance(coin)
        if res["ret_code"] == 0:
            self.logger.info(
                f"Successfully got the account balance: {res['result']}"
            )
        else:
            self.logger.info("Failed to get account balance")

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
                "No change in leverage - new leverage was the same as the" +
                " old leverage"
            )
        else:
            self.logger.info("Failed to change leverage")

    def before_termination(self, *args, **kwargs):
        """Strategy Manager calls this before terminating a running strategy"""
        self.logger.info("inside before_termination()")

        # Do not delete this line:
        super().before_termination()


if __name__ == "__main__":
    try:

        # Change name and version of your strategy:
        name = "NebStrategy"
        version = "0.1.0"

        # Do not delete these lines:
        strategy = NebStrategy(name, version)
        strategy.logger.info("Successfully initialized strategy")
        strategy.before_start()
        strategy.start()
        strategy.before_termination()
    except Exception as err:
        if strategy is not None:
            strategy.logger.exception(err)
            if not strategy.has_called_before_termination:
                strategy.before_termination()