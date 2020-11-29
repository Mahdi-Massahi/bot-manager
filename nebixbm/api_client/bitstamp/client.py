from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
import json
import csv

from nebixbm.log.logger import create_logger, get_file_name


class BitstampException(Exception):
    """Bitstamp internal exceptions"""
    pass


class RequestType:
    """Request types enum class"""

    GET = 0
    POST = 1


class BitstampClient:
    """A Bitstamp api client implementation"""

    def __init__(self, secret, api_key, req_timeout):
        if [i for i in (secret, api_key, req_timeout) if i is None]:
            raise TypeError

        self.name = "BitstampClient"
        filename = get_file_name(self.name, "")
        self.logger, self.log_filepath = create_logger(filename, filename)
        self.endpoint = "https://www.bitstamp.net/api/"
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
            resp_list = json.loads(resp.text)
            # TODO check ret code for Bitstamp
            # if "code" in resp_list:
            #     raise BinanceException(resp_list['code'])
            # else:
            #     raise
        except requests.exceptions.ConnectionError:
            raise
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.RequestException:
            raise
        except Exception as ex:
            self.logger.warning(ex)  # TODO Check it
            raise BitstampException(ex)

        else:  # no exceptions:

            resp_list = json.loads(resp.text)
            # self.logger.debug(resp_list)
            # if str(resp_list['ret_code']) != '0':
            #     raise BitstampException(resp_list['ext_code'])
            return resp_list

    def get_kline(
        self, symbol, interval, start_time=None, end_time=None, limit=1,
    ):
        """Get kline data
          [{
            "high": "19416.64",
            "timestamp": "1606230000",
            "volume": "17.61453843",
            "low": "19395.34",
            "close": "19416.64",
            "open": "19407.47"
          }]
        """

        relative_url = "v2/ohlc/{currency_pair}/"
        relative_url = relative_url.replace("{currency_pair}", symbol.lower())
        params = {
            "step": interval,
            "start": start_time,
            "end": end_time,
            "limit": limit,
        }
        res = self.send_request(
            req_type=RequestType.GET,
            relative_url=relative_url,
            params=params,
            is_signed=False,
        )
        return res

    def kline_to_csv(self, symbol, interval, limit, filepath):
        """Get kline data and write to csv file at given filepath"""
        klines = self.get_kline(symbol, interval=interval, limit=limit)
        if klines:
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
            for c, k in enumerate(klines["data"]["ohlc"]):
                results.append(
                    [c + 1, k["open"], k["close"], k["high"], k["low"],
                     k["volume"], int(k["timestamp"])]
                )

            with open(filepath, "w+", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(results[:-1])  # exclude last kline
                self.logger.debug("Successfully wrote results to file")

        else:
            self.logger.warning(
                "Something was wrong with API response. " +
                f"The response was: {klines}"
            )
            return False
        return True

    def multi_kline_to_csv(self, symbol, interval, limit,
                     filepath, start, end=None):
        """Get multi kline data and write to csv file at given filepath"""
        results = [
            [
                "Index",
                "Open",
                "Close",
                "High",
                "Low",
                "Volume",
                "Date",
            ]
        ]
        filename = ""
        if end is None:
            end = int(datetime.utcnow().timestamp())

        du = end - start
        if du < 0:
            raise Exception("Not a valid request.")

        cr = int(du/(interval*limit))

        for cr_c in range(0, cr+1):
            print("Request no. ", cr_c, f"({round(cr_c/(cr)*100, 2)}%)")
            st = (cr_c*interval*limit)+start
            klines = self.get_kline(symbol=symbol,
                                    interval=interval,
                                    limit=limit,
                                    start_time=st)

            if not klines:
                self.logger.warning(
                    "Something was wrong with API response. " +
                    f"The response was: {klines}"
                )
                raise Exception("Not a valid data.")

            self.logger.debug(
                f"Writing kline csv results for symbol:{symbol}, " +
                f"interval:{interval}..."
            )

            for c, k in enumerate(klines["data"]["ohlc"]):
                k_timestamp = datetime.fromtimestamp(int(k["timestamp"]),
                                                     tz=timezone.utc)
                k_datetime = k_timestamp.strftime("%y/%m/%d - %H:%M")

                if int(k["timestamp"]) <= end:
                    results.append(
                        [c + cr_c * limit + 1,
                         k["open"], k["close"], k["high"], k["low"],
                         k["volume"], k_datetime]
                    )
        filename = f"KL-{symbol.upper()}-{interval/60}m-C" + \
                   str(len(results)-1) + ".csv"

        with open(filepath + filename, "w+", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(results)  # exclude last kline
            self.logger.debug("Successfully wrote results to file")

        return True
