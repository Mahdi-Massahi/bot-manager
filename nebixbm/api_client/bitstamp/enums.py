class Symbol:
    """Symbol Enum"""

    name = "symbol"

    BTCUSD = "btcusd"
    XRPUSD = "xrpusd"
    ETHUSD = "ethusd"

    @staticmethod
    def value():
        return [
            Symbol.BTCUSD,
            Symbol.XRPUSD,
            Symbol.ETHUSD,
        ]


class Interval:
    """Interval Enum"""

    name = "interval"

    i14400 = "14400"
    i300 = "300"
    i60 = "60"

    @staticmethod
    def values():
        """Get all interval values"""

        return [
            Interval.i60,
            Interval.i300,
            Interval.i14400,
        ]
