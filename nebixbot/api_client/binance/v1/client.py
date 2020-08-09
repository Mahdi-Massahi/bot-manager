from nebixbot.api_client.base_client import BaseClient


class BinanceClient(BaseClient):
    """A Binance api client implementation"""

    def __init__(self):
        super().__init__('BinanceClient', 'v1')
