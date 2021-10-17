from nebixbm.command_center.bot.ahaeds_inverse_btcusd_4h import ahaeds_inverse_btcusd_4h


def get_available_bots():
    return {
        f"ahaeds_inverse_btcusd_4h {ahaeds_inverse_btcusd_4h.version}": ahaeds_inverse_btcusd_4h,
        }
