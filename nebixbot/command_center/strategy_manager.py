import os
import signal
import subprocess

from nebixbot.log.logger import create_logger
from nebixbot.command_center.strategy.sample_strategy.sample_strategy import (
    SampleStrategy,
)


class StrategyManager:
    """The strategy control unit"""

    def __init__(self):
        self.strategy_data_filename = '.st.dat'
        self.logger = create_logger('strategy_manager', 'strategy_manager')
        self.load_strategies()

    def load_strategies(self):
        """Load used strategies"""
        self.strategies = {
            'ss': SampleStrategy
        }

        return self.strategies

    def get_strategy_data(self):
        pass

    def get_running_strategies(self):
        """Return running(started) strategies"""
        pass

    def run(self, strategy_name) -> bool:
        """Run(start) given strategy"""
        if strategy_name not in self.strategies:
            return False
        else:
            strategy = self.strategies[strategy_name]
            try:
                strategy.before_start()
                strategy.start()
                # TODO: add to .st.dat 
            except Exception as err:
                # TODO: log error
                return False
        return True

    def terminate(self, strategy_name) -> bool:
        """"Terminate(stop) given strategy"""
        pass
