from urllib.parse import urljoin
import requests
import json


class RequestType:
    """Request types enum class"""

    GET = 0
    POST = 1


class BinanceClient:
    """A Binance api client implementation"""

    def __init__(self, secret, api_key, req_timeout):
        if [i for i in (secret, api_key, req_timeout) if i is None]:
            raise TypeError

        self.name = "BinanceClient"
        self.endpoint = "https://api.binance.com/"
        self.secret = secret
        self.api_key = api_key
        # timeout seconds if no response from server is received:
        self.request_timeout = req_timeout

    def create_query_url(self, url, params):
        """Create url query form parameters"""
        if not url:
            return ""
        return (
            url
            + "?"
            + "&".join(
                [
                    f"{str(k)}={str(v)}"
                    for k, v in sorted(params.items(), reverse=True)
                    if v is not None
                ]
            )
        )

    def send_request(self, req_type, relative_url, params, is_signed):
        """Send request to a url and return response/exceptions"""

        url = urljoin(self.endpoint, relative_url)
        if is_signed:
            pass
        else:
            if params:
                url_query = self.create_query_url(url, params)
            else:
                url_query = url
        try:
            if req_type == RequestType.GET:
                resp = requests.get(url_query, timeout=self.request_timeout)
            elif req_type == RequestType.POST:
                resp = requests.post(url_query, timeout=self.request_timeout)
            else:
                raise Exception("Invalid RequestType")
            resp.raise_for_status()  # check for Http errors

        except requests.exceptions.HTTPError:
            raise
        except requests.exceptions.ConnectionError:
            raise
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.RequestException:
            raise

        else:  # no exceptions:
            resp_dict = json.loads(resp.text)

            return resp_dict

    def get_kline(
        self, symbol, interval, start_time=None, end_time=None, limit=None,
    ):
        """Get kline data
        reutrns [[
            0  'Open time',
            1  'Open',
            2  'High',
            3  'Low',
            4  'Close',
            5  'Volume',
            6  'Close time',
            7  'Quote asset volume',
            8  'Number of trades',
            9  'Taker buy base asset volume',
            10 'Taker buy quote asset volume',
            11 'Ignore'
        ]]
        """

        relative_url = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )

        return res
