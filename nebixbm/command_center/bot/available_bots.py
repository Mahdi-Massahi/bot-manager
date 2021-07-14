from nebixbm.command_center.bot.neb_bot import neb_bot
from nebixbm.command_center.bot.ahaeds_1m import ahaeds_1m


def get_available_bots():
    return {
        f"neb_bot {neb_bot.version}": neb_bot,
        f"ahaeds_1m TNMS {ahaeds_1m.version}": ahaeds_1m,
        }
