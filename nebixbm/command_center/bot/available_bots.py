# from nebixbm.command_center.bot.template_bot import (
#     template_bot,
# )
# from nebixbm.command_center.bot.sample_bot import sample_bot

# from nebixbm.command_center.bot.sample_bot2 import sample_bot2
# from nebixbm.command_center.bot.scheduled_bot import (
#     scheduled_bot,
# )
# from nebixbm.command_center.bot.redis_bot import redis_bot
# from nebixbm.command_center.bot.client_test_bot import (
#     client_test_bot,
# )
# from nebixbm.command_center.bot.kline_bot import kline_bot
# from nebixbm.command_center.bot.binance_test_bot import binance_test_bot
# from nebixbm.command_center.bot.order_bot import order_bot
from nebixbm.command_center.bot.neb_bot import neb_bot
# from nebixbm.command_center.bot.large_kline_bot import large_kline_bot
from nebixbm.command_center.bot.email_bot import email_bot
from nebixbm.command_center.bot.timeout_bot import timeout_bot


def get_available_bots():
    return {
        # f"template_bot": template_bot,
        # f"sample_bot": sample_bot,
        # f"sample_bot2": sample_bot2,
        # f"scheduled_bot": scheduled_bot,
        # f"redis_bot": redis_bot,
        # f"client_test_bot": client_test_bot,
        # f"kline_bot": kline_bot,
        # f"binance_test_bot": binance_test_bot,
        # f"order_bot": order_bot,
        # f"large_kline_bot": large_kline_bot,
        f"email_bot {email_bot.version}": email_bot,
        f"neb_bot {neb_bot.version}": neb_bot,
        f"timeout_bot {timeout_bot.version}": timeout_bot,
    }
