class Symbol:
    """Symbol Enum"""

    name = "symbol"

    BTCUSDT = "BTCUSDT"
    ETHUSDT = "ETHUSDT"
    EOSUSDT = "EOSUSDT"
    XRPUSDT = "XRPUSDT"


class Interval:
    """Interval Enum"""

    name = "interval"

    i1m = "1m"
    i3m = "3m"
    i5m = "5m"
    i15m = "15m"
    i30m = "30m"
    i1h = "1h"
    i2h = "2h"
    i4h = "4h"
    i6h = "6h"
    i8h = "8h"
    i12h = "12h"
    i1d = "1d"
    i3d = "3d"
    i1w = "1w"
    i1M = "1M"

    @staticmethod
    def values():
        """Get all interval values"""

        return [
            Interval.i1m,
            Interval.i3m,
            Interval.i5m,
            Interval.i15m,
            Interval.i30m,
            Interval.i1h,
            Interval.i2h,
            Interval.i4h,
            Interval.i6h,
            Interval.i8h,
            Interval.i12h,
            Interval.i1d,
            Interval.i3d,
            Interval.i1w,
            Interval.i1M,
        ]
