from nebixbm.command_center.bot.ahaeds_inverse_btcusd_4h import ahaeds_inverse_btcusd_4h
from nebixbm.command_center.bot.ahaeds_linear_btcusdt_4h import ahaeds_linear_btcusdt_4h


def get_available_bots():
    return {
        f"ahaeds_inverse_btcusd_4h {ahaeds_inverse_btcusd_4h.version}": ahaeds_inverse_btcusd_4h,
        f"ahaeds_linear_btcusdt_4h {ahaeds_linear_btcusdt_4h.version}": ahaeds_linear_btcusdt_4h,
        }
