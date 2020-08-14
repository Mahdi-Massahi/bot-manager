import hmac
from urllib.parse import urljoin
import requests
import json
import datetime
from datetime import timezone


def timestamp_to_datetime(timestamp):
    """Convert timestamp to datetime object"""
    return datetime.datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt):
    """Convert datetime object to timestamp"""
    return dt.timestamp()


def reformat_timestamp(ts, to_mili=True):
    """Reformat timestamp and remove miliseconds"""
    return str(int(float(ts) * 1000)) if to_mili else str(int(float(ts)))


class RequestType:
    """Request types enum class"""

    GET = 0
    POST = 1


class BybitClient:
    """A Bybit api client implementation"""

    def __init__(self, is_testnet, secret, api_key, req_timeout):

        if [
            i for i in (is_testnet, secret, api_key, req_timeout) if i is None
        ]:
            raise TypeError

        self.name = "BybitClient"
        # timeout seconds if no response from server is received:
        self.is_testnet = is_testnet
        if is_testnet:
            self.endpoint = "https://api-testnet.bybit.com"
        else:
            self.endpoint = "https://api.bybit.com"
        self.secret = secret
        self.api_key = api_key
        self.request_timeout = req_timeout

    def get_signature(self, req_params):
        """Create signature from parameters and secret"""
        _val = "&".join(
            [
                f"{str(k)}={str(v)}"
                for k, v in sorted(req_params.items())
                if k != "sign" and v is not None
            ]
        )
        return str(
            hmac.new(
                bytes(self.secret, "utf-8"),
                bytes(_val, "utf-8"),
                digestmod="sha256",
            ).hexdigest()
        )

    def create_query_url(self, url, params):
        """Create query form parameters"""
        if not url:
            return ''
        return (
            url
            + "?"
            + "&".join(
                [
                    f"{str(k)}={str(v)}"
                    for k, v in sorted(params.items())
                    if v is not None
                ]
            )
        )

    def send_request(self, req_type, relative_url, params, is_signed):
        """Send request to a url and return response/exceptions"""
        url = urljoin(self.endpoint, relative_url)
        if is_signed:
            if params:
                params["api_key"] = self.api_key
                if "from" not in params:  # because bybit api sucks
                    timestamp = self.get_server_timestamp()
                    params["timestamp"] = timestamp
                params["sign"] = self.get_signature(params)
                url_query = self.create_query_url(url, params)
            else:
                params = {}
                params["api_key"] = self.api_key
                timestamp = self.get_server_timestamp()
                if "from" not in params:  # because bybit api sucks
                    params["timestamp"] = timestamp
                    params["sign"] = self.get_signature(params)
                url_query = self.create_query_url(url, params)
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
            # TODO: error in status code
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

    def get_server_timestamp(self):
        """Get server timestamp"""
        relative_url = "/v2/public/time"
        res = self.send_request(
            RequestType.GET,
            relative_url=relative_url,
            params=None,
            is_signed=False,
        )

        return reformat_timestamp(res["time_now"])

    def get_kline_open_timestamps(self, symbol, interval, to_datetime=False):
        """Get next, last kline opening timestamp and their delta"""

        if isinstance(interval, int):
            from_dt = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(minutes=interval*2)
        elif isinstance(interval, str):
            if interval == 'D':
                from_dt = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=2)
            elif interval == 'W':
                from_dt = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(weeks=2)
            elif interval == 'M':  # 2 months < 10 weeks
                from_dt = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(weeks=10)
            elif interval == 'Y':
                today = datetime.datetime.today()
                next_year_dt = datetime.datetime(today.year + 1, 1, 3)
                next_year_ts = int(datetime_to_timestamp(next_year_dt))
                last_year_dt = datetime.datetime(today.year, 1, 3)
                last_year_ts = int(datetime_to_timestamp(last_year_dt))
                delta = int(next_year_ts - last_year_ts)
                return (
                    next_year_dt if to_datetime else next_year_ts,
                    last_year_dt if to_datetime else last_year_ts,
                    delta,
                )
        else:
            raise TypeError("Interval type not correct")

        limit = 2
        res = self.get_kline(symbol, interval, from_dt, limit)

        first_kline_open_timestamp = res['result'][0]['open_time']
        second_kline_open_timestamp = res['result'][1]['open_time']
        delta = second_kline_open_timestamp - first_kline_open_timestamp
        next_kline_open_timestamp = second_kline_open_timestamp + delta
        last_kline_open_timestamp = second_kline_open_timestamp

        return (
            timestamp_to_datetime(next_kline_open_timestamp) if to_datetime else next_kline_open_timestamp,
            timestamp_to_datetime(last_kline_open_timestamp) if to_datetime else last_kline_open_timestamp,
            delta,
        )

    def get_order_book(self, symbol):
        """Get order book"""
        relative_url = "/v2/public/orderBook/L2"
        params = {"symbol": symbol}

        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )
        return res

    def get_kline(self, symbol, interval, from_dt, limit):
        """Get kline"""
        relative_url = '/v2/public/kline/list'
        # Convert datetime to reformatted timestamps:
        from_ts = reformat_timestamp(datetime_to_timestamp(from_dt), False)
        params = {
            'symbol': symbol,
            'interval': interval,
            'from': from_ts,
            'limit': limit
        }

        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )
        return res

    def get_wallet_balance(self, coin):
        """Get wallet balance info"""
        relative_url = "/v2/private/wallet/balance"
        params = {}
        if coin:
            params = {"coin": coin}

        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )
        return res

    def change_user_leverage(self, symbol, leverage):
        """Chage user leverage"""
        relative_url = "/user/leverage/save"
        params = {"symbol": symbol, "leverage": leverage}

        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )
        return res
