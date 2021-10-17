from nebixbm.command_center.bot.neb_bot import neb_bot


def get_available_bots():
    return {
        f"neb_bot {neb_bot.version}": neb_bot,
        }
