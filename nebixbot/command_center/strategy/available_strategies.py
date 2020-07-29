from nebixbot.command_center.strategy.template_strategy import (
    template_strategy,
)
from nebixbot.command_center.strategy.sample_strategy import sample_strategy
from nebixbot.command_center.strategy.sample_strategy2 import sample_strategy2
from nebixbot.command_center.strategy.scheduled_strategy import (
    scheduled_strategy,
)


def get_available_strategies():
    return {
        "template_strategy": template_strategy,
        "sample_strategy": sample_strategy,
        "sample_strategy2": sample_strategy2,
        "scheduled_strategy": scheduled_strategy,
    }
