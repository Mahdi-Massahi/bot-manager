import hmac
from urllib.parse import urljoin
import requests
import json
import datetime
from datetime import timezone


class BybitException(Exception):
    """Internal Bybit exceptions"""
    pass


def timestamp_to_datetime(timestamp):
    """Convert timestamp to datetime object"""
    return datetime.datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt):
    """Convert datetime object to timestamp"""
    return dt.timestamp()


def reformat_timestamp(ts, to_mili=True):
    """Reformat timestamp and remove miliseconds if needed"""
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
        self.is_testnet = is_testnet
        if is_testnet:
            self.endpoint = "https://api-testnet.bybit.com"
        else:
            self.endpoint = "https://api.bybit.com"
        self.secret = secret
        self.api_key = api_key
        # timeout seconds if no response from server is received:
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
            return ""
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
            raise
        except requests.exceptions.ConnectionError:
            raise
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.RequestException:
            raise

        else:  # no exceptions:
            resp_dict = json.loads(resp.text)
            if str(resp_dict['ret_code']) != '0':
                raise BybitException(resp_dict['ext_code'])
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
            from_dt = datetime.datetime.now(
                tz=timezone.utc
            ) - datetime.timedelta(minutes=interval * 2)
        elif isinstance(interval, str):
            if interval == "D":
                from_dt = datetime.datetime.now(
                    tz=timezone.utc
                ) - datetime.timedelta(days=2)
            elif interval == "W":
                from_dt = datetime.datetime.now(
                    tz=timezone.utc
                ) - datetime.timedelta(weeks=2)
            elif interval == "M":  # 2 months < 10 weeks
                from_dt = datetime.datetime.now(
                    tz=timezone.utc
                ) - datetime.timedelta(weeks=10)
            elif interval == "Y":
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

        first_kline_open_timestamp = res["result"][0]["open_time"]
        second_kline_open_timestamp = res["result"][1]["open_time"]
        delta = second_kline_open_timestamp - first_kline_open_timestamp
        next_kline_open_timestamp = second_kline_open_timestamp + delta
        last_kline_open_timestamp = second_kline_open_timestamp

        return (
            timestamp_to_datetime(next_kline_open_timestamp)
            if to_datetime
            else next_kline_open_timestamp,
            timestamp_to_datetime(last_kline_open_timestamp)
            if to_datetime
            else last_kline_open_timestamp,
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

    def get_public_trading_records(self, symbol, from_ts=None, limit=None):
        """Get recent trades"""

        relative_url = "/v2/public/trading-records"
        params = {
            "symbol": symbol,
            "from_ts": from_ts,
            "limit": limit,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )

        return res

    def get_kline(self, symbol, interval, from_dt, limit):
        """Get kline"""
        relative_url = "/v2/public/kline/list"
        # Convert datetime to reformatted timestamps:
        from_ts = reformat_timestamp(datetime_to_timestamp(from_dt), False)
        params = {
            "symbol": symbol,
            "interval": interval,
            "from": from_ts,
            "limit": limit,
        }

        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )
        return res

    def place_order(
        self,
        side,
        symbol,
        order_type,
        qty,
        time_in_force,
        price=None,
        take_profit=None,
        stop_loss=None,
        reduce_only=None,
        close_on_trigger=None,
        order_link_id=None,
    ):
        """Place Active Order"""

        relative_url = "/v2/private/order/create"
        params = {
            "side": side,
            "symbol": symbol,
            "order_type": order_type,
            "qty": qty,
            "price": price,
            "time_in_force": time_in_force,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "reduce_only": reduce_only,
            "close_on_trigger": close_on_trigger,
            "order_link_id": order_link_id,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_active_order(
        self,
        order_id=None,
        order_link_id=None,
        symbol=None,
        order=None,
        page=None,
        limit=None,
        order_status=None,
    ):
        """Get Active Order"""

        relative_url = "/open-api/order/list"
        params = {
            "order_id": order_id,
            "order_link_id": order_link_id,
            "symbol": symbol,
            "order": order,
            "page": page,
            "limit": limit,
            "order_status": order_status,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def cancel_active_order(self, symbol, order_id, order_link_id=None):
        """Cancel Active Order"""

        relative_url = "/v2/private/order/cancel"
        params = {
            "symbol": symbol,
            "order_id": order_id,
            "order_link_id": order_link_id,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def cancel_all_active_orders(self, symbol):
        """Cancel All Active Orders"""

        relative_url = "/v2/private/order/cancelAll"
        params = {
            "symbol": symbol,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def replace_active_order(
        self, order_id, symbol, p_r_qty=None, p_r_price=None
    ):
        """Replace Active Order"""

        relative_url = "/open-api/order/replace"
        params = {
            "symbol": symbol,
            "order_id": order_id,
            "symbol": symbol,
            "p_r_qty": p_r_qty,
            "p_r_price": p_r_price,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_position(self, symbol):
        """Get position list"""

        relative_url = "/v2/private/position/list"
        params = {
            "symbol": symbol,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def change_margin(self, symbol, margin):
        """Update margin"""

        relative_url = "/position/change-position-margin"
        params = {
            "symbol": symbol,
            "margin": margin,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def set_trailing_stop(
        self,
        symbol,
        take_profit=None,
        stop_loss=None,
        trailing_stop=None,
        new_trailing_active=None,
    ):
        """Set take profit, stop loss, and trailing stop
        for your open position.
        """

        relative_url = "/open-api/position/trading-stop"
        params = {
            "symbol": symbol,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "trailing_stop": trailing_stop,
            "new_trailing_active": new_trailing_active,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_leverage(self):
        """Get user leverage"""

        relative_url = "/user/leverage"
        params = None
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

    def get_user_trade_records(
        self,
        symbol,
        order_id=None,
        start_time=None,
        page=None,
        limit=None,
        order=None,
    ):
        """Get user's trading records. The results are ordered in
        ascending order (the first item is the oldest).
        """

        relative_url = "/v2/private/execution/list"
        params = {
            "symbol": symbol,
            "order_id": order_id,
            "start_time": start_time,
            "page": page,
            "limit": limit,
            "order": order,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_closed_pnl(
        self,
        symbol,
        start_time,
        end_time,
        exec_type,
        page,
        limit,
    ):
        """Get user's closed profit and loss records. The results are ordered
        in descending order (the first item is the latest).
        """

        relative_url = "/v2/private/trade/closed-pnl/list"
        params = {
            "symbol": symbol,
            "start_time": start_time,
            "end_time": end_time,
            "exec_type": exec_type,
            "page": page,
            "limit": limit,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_wallet_balance(self, coin=None):
        """Get wallet balance info."""

        relative_url = "/v2/private/wallet/balance"
        params = {
            "coin": coin,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_announcement(self):
        """Get Bybit OpenAPI announcements in the last 30 days by reverse order."""

        relative_url = "/v2/public/announcement"
        params = None
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )

        return res
