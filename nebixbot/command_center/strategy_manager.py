import os
import signal
import subprocess
import psutil

from nebixbot.log.logger import create_logger, get_log_fname_path
from nebixbot.command_center.strategy.sample_strategy import sample_strategy
from nebixbot.command_center.strategy.sample_strategy2 import sample_strategy2


class StrategyManager:
    """The strategy control unit"""

    def __init__(self):
        self.strategy_data_filename = '.stm.dat'
        self.logger, self.log_filepath = create_logger(
            'strategy_manager',
            'strategy_manager'
        )
        self.load_strategies()

    def log_logfile_path(self):
        """Log logfile path into logger"""
        self.logger.info(f"Logger: {self.log_filepath}")

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

    def get_strategy_pid(self, strategy_id):
        """Get strategy pid"""
        pass

    def run(self, strategy_name) -> bool:
        """Run(start) given strategy"""
        if strategy_name not in self.strategies:
            return False
        else:
            strategy = self.strategies[strategy_name]
            filepath = self.abs_strategy_filepath(strategy)
            try:
                proc = subprocess.Popen(
                    f"python3 {filepath}",
                    shell=True,
                    preexec_fn=os.setsid
                )
                self.logger.info(f'Process Created (pid:{proc.pid})')
                # TODO: add to .st.dat
                # dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # id, pid, name, run_time
            except Exception as err:
                self.logger.error(err)
                return False
        return True

    def terminate(self, strategy_id) -> bool:
        """"Terminate(stop) given strategy"""
        pid = get_strategy_pid(strategy_id)
        if not psutil.pid_exists(pid):
            self.logger.error(err)
            return False
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            return True
        except Exception as err:
            self.logger.error(err)
        return False
