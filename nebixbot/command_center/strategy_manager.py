import os
import signal
import subprocess
from datetime import datetime

from nebixbot.log.logger import create_logger
from nebixbot.command_center.strategy.sample_strategy import sample_strategy
from nebixbot.command_center.strategy.sample_strategy2 import sample_strategy2


class StrategyManager:
    """The strategy control unit"""

    def __init__(self):
        self.strategy_data_filename = '.st.dat'
        self.logger = create_logger('strategy_manager', 'strategy_manager')
        self.load_strategies()

    def load_strategies(self):
        """Load used strategies"""
        self.strategies = {
            'sample_strategy': sample_strategy,
            'sample_strategy2': sample_strategy2,
        }

        return self.strategies

    def get_strategy_data(self):
        # TODO: load .st.dat, compare it with running pids
        # and request restart if needed!
        pass

    def get_running_strategies(self):
        """Return running(started) strategies"""
        pass

    def abs_strategy_filepath(self, strategy_module):
        """Return absolute path to strategy file"""
        return os.path.abspath(strategy_module.__file__)

    def run(self, strategy_name) -> bool:
        """Run(start) given strategy"""
        if strategy_name not in self.strategies:
            return False
        else:
            strategy = self.strategies[strategy_name]
            filepath = self.strategy_filepath(strategy)
            try:
                proc = subprocess.Popen(
                    f"python3 {filepath}",
                    stdout=subprocess.PIPE,
                    shell=True,
                    preexec_fn=os.setsid
                )
                self.logger.info(f'proc={proc}', pid={proc.pid})
                # Popen"python3 -m <strategy>"
                # TODO: add to .st.dat
                # dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # id, pid, name, run_time
            except Exception as err:
                self.logger.error(err)
                return False
        return True

    def terminate(self, strategy_name) -> bool:
        """"Terminate(stop) given strategy"""
        pass
