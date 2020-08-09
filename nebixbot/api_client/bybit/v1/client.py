from nebixbot.api_client.base_client import BaseClient


class BybitClient(BaseClient):
    """A Bybit api client implementation"""

    def __init__(self):
        super().__init__('BybitClient', 'v1')
