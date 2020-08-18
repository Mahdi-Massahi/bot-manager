from nebixbm.command_center.bot.template_bot import (
    template_bot,
)
from nebixbm.command_center.bot.sample_bot import sample_bot
from nebixbm.command_center.bot.sample_bot2 import sample_bot2
from nebixbm.command_center.bot.scheduled_bot import (
    scheduled_bot,
)
from nebixbm.command_center.bot.redis_bot import redis_bot
from nebixbm.command_center.bot.client_test_bot import (
    client_test_bot,
)
from nebixbm.command_center.bot.kline_bot import kline_bot


def get_available_bots():
    return {
        "template_bot": template_bot,
        "sample_bot": sample_bot,
        "sample_bot2": sample_bot2,
        "scheduled_bot": scheduled_bot,
        "redis_bot": redis_bot,
        "client_test_bot": client_test_bot,
        "kline_bot": kline_bot,
    }
