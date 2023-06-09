import hmac
from urllib.parse import urljoin
import requests
import json
import datetime
from datetime import timezone
import csv
from time import time

from nebixbm.api_client.bybit import enums as bybit_enum
from nebixbm.log.logger import create_logger, get_file_name


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
        filename = get_file_name(self.name, "")
        self.logger, self.log_filepath = create_logger(filename, filename)
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
        self.logger.debug(url_query)
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
            # reduce only failed : 30063
            # wrong stop-loss price : 30028
            # API Expired : 33004
            resp_dict = json.loads(resp.text)
            # self.logger.debug(resp_dict)
            if str(resp_dict['ret_code']) == '33004':
                raise BybitException("Expired API.")
            if (str(resp_dict['ret_code']) != '0' and
                    str(resp_dict['ret_code']) != '30063' and
                    # TODO this is because of error in Bybit's testnet
                    str(resp_dict['ret_code']) != '30052' and
                    str(resp_dict['ret_code']) != '30028' and
                    str(resp_dict['ret_code']) != '34015'):
                raise BybitException(resp_dict)
            return resp_dict

    def kline_to_csv(self, symbol, limit, interval, filepath):
        """Get kline data and write to csv file at given filepath"""
        # if interval == bybit_enum.Interval.Y:
        #     return None
        # (
        #     next_kline_ts,
        #     last_kline_ts,
        #     delta,
        # ) = self.get_kline_open_timestamps(symbol, interval)
        # from_ts = next_kline_ts - delta * limit
        # from_ts = 0 if from_ts < 0 else from_ts
        # from_dt = timestamp_to_datetime(from_ts)
        #
        # res = self.get_kline(symbol, interval, from_dt, limit)
        from_s = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=interval * limit)
        res = self.get_kline(
            symbol=symbol,
            interval=interval,
            limit=limit,
            from_dt=from_s)

        # if results exits in response:
        if res and "result" in res and res["result"]:
            self.logger.debug(
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
                writer.writerows(results)  # don't exclude last kline
                # writer.writerows(results[:-1])  # exclude last kline
                self.logger.debug("Successfully wrote results to file.")
                self.logger.debug("Bybit data summary:\n"
                                  f'Start timestamp: \t{results[1][6]}\n'
                                  f'End timestamp:   \t{results[-1][6]}\n'
                                  f'Datapoint number:\t{len(results)}')
                return True

        else:
            self.logger.warning(
                "Something was wrong with API response. " +
                f"The response was: {res}"
            )
            return False

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
            ) - datetime.timedelta(minutes=interval * 3)
        elif isinstance(interval, str):
            if interval == "D":
                from_dt = datetime.datetime.now(
                    tz=timezone.utc
                ) - datetime.timedelta(days=3)
            elif interval == "W":
                from_dt = datetime.datetime.now(
                    tz=timezone.utc
                ) - datetime.timedelta(weeks=3)
            elif interval == "M":  # 2 months < 10 weeks
                from_dt = datetime.datetime.now(
                    tz=timezone.utc
                ) - datetime.timedelta(weeks=15)
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

        limit = 3
        res = self.get_kline(symbol, interval, from_dt, limit)
        try:
            first_kline_open_timestamp = res["result"][1]["open_time"]
            second_kline_open_timestamp = res["result"][2]["open_time"]
        except IndexError:
            self.logger.warning(
                "Index Error fixed! Wanted 3 klines, but got 2; was going" +
                " to cause an Error"
            )
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
        """Get Bybit OpenAPI announcements in the
         last 30 days by reverse order.
         """

        relative_url = "/v2/public/announcement"
        params = None
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )
        return res

    def query_active_order(
        self, symbol, order_id, order_link_id=None,
    ):
        """Query real-time active order information."""

        relative_url = "/v2/private/order"
        params = {
            "order_id": order_id,
            "order_link_id": order_link_id,
            "symbol": symbol,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def change_stoploss_trigger_by(self,
                                   symbol,
                                   take_profit=None,
                                   stop_loss=None,
                                   trailing_stop=None,
                                   tp_trigger_by=None,
                                   sl_trigger_by=None,
                                   new_trailing_active=None,
                                   ):

        relative_url = "/open-api/position/trading-stop"
        params = {
            "symbol": symbol,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "trailing_stop": trailing_stop,
            "tp_trigger_by": tp_trigger_by,
            "sl_trigger_by": sl_trigger_by,
            "new_trailing_active": new_trailing_active,
        }
        res = self.send_request(
            req_type=RequestType.POST,
            relative_url=relative_url,
            params=params,
            is_signed=True,
        )

        return res

    def get_closed_profit_and_loss(self,
                                   symbol,
                                   start_time=None,
                                   end_time=None,
                                   exec_type=None,
                                   page=1,
                                   limit=20):

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
