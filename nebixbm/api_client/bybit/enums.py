class Side:

    name = "side"

    BUY = "Buy"
    SELL = "Sell"
    NONE = "None"


class Symbol:

    name = "symbol"

    BTCUSD = "BTCUSD"
    ETHUSD = "ETHUSD"
    EOSUSD = "EOSUSD"
    XRPUSD = "XRPUSD"

    @staticmethod
    def value():
        return [
            Symbol.BTCUSD,
            Symbol.ETHUSD,
            Symbol.EOSUSD,
            Symbol.XRPUSD,
        ]


class Coin:

    name = "coin"

    BTC = "BTC"
    ETH = "ETH"
    EOS = "EOS"
    XRP = "XRP"
    USDT = "USDT"

    @staticmethod
    def value():
        return [
            Coin.BTC,
            Coin.ETH,
            Coin.EOS,
            Coin.XRP,
            Coin.USDT,
        ]


class OrderType:

    name = "order_type"

    LIMIT = "Limit"
    MARKET = "Market"


class Interval:
    """Interval Enum"""

    name = "interval"

    i1 = 1
    i3 = 3
    i5 = 5
    i15 = 15
    i30 = 30
    i60 = 60
    i120 = 120
    i240 = 240
    i360 = 360
    i720 = 720
    D = "D"
    W = "W"
    M = "M"
    Y = "Y"

    @staticmethod
    def values():
        """Get all interval values"""

        return [
            Interval.i1,
            Interval.i3,
            Interval.i5,
            Interval.i15,
            Interval.i30,
            Interval.i60,
            Interval.i120,
            Interval.i240,
            Interval.i360,
            Interval.i720,
            Interval.D,
            Interval.W,
            Interval.M,
            Interval.Y,
        ]


class TimeInForce:
    """Time in force"""

    name = "time_in_force"

    GOODTILLCANCEL = "GoodTillCancel"
    IMMEDIATEORCANCEL = "ImmediateOrCancel"
    FILLORKILL = "FillOrKill"
    POSTONLY = "PostOnly"


class TriggerBy:
    """Trigger By"""

    name = "trigger_by"

    LASTPRICE = "LastPrice"
    INDEXPRICE = "IndexPrice"
    MARKPRICE = "MarkPrice"


class ExecType:
    """Exec type (exec_type)"""

    name = "Exec type"

    TRADE = "Trade"
    ADLTRADE = "AdlTrade"
    FUNDING = "Funding"
    BUSTTRADE = "BustTrade"



