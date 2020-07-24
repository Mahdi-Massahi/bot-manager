import os
import signal
import subprocess
import psutil
import uuid
import pickle
from datetime import datetime

from nebixbot.other.tcolors import Tcolors
from nebixbot.log.logger import create_logger, get_log_fname_path
from nebixbot.command_center.strategy.sample_strategy import sample_strategy
from nebixbot.command_center.strategy.sample_strategy2 import sample_strategy2


class StrategyManager:
    """The strategy control unit"""

    def __init__(self):
        head, _ = os.path.split(os.path.abspath(__file__))
        self.strategy_data_filename = os.path.join(head, 'stm.dat')
        self.logger, self.log_filepath = create_logger(
            'strategy_manager',
            'strategy_manager'
        )
        self.strategies = self.init_strategies()

    def init_strategies(self):
        """Load used strategies"""
        return {
            'sample_strategy': sample_strategy,
            'sample_strategy2': sample_strategy2,
        }

    def log_logfile_path(self):
        """Log logfile path into logger"""
        self.logger.info(f"Logger: {self.log_filepath}")

    def print_available_strategies(self) -> dict:
        """Print available strategies"""
        print(f"{Tcolors.HEADER}Available Strategies:{Tcolors.ENDC}")
        for strategy_name in self.strategies.keys():
            print(
                f'\t- {Tcolors.BOLD}{strategy_name}{Tcolors.ENDC}:',
                self.strategies[strategy_name].__name__
            )

    def print_running_strategies(self) -> dict:
        """Print running strategies"""
        print(f"{Tcolors.HEADER}Running Strategies:{Tcolors.ENDC}")
        print(
            '\tformat: <unique id>:' +
            '[<pid>, <strategy name>, <start date/time>]'
        )
        details = self.load_detail()
        if details:
            found_running = False
            for id in details.keys():
                pid = details[id][0]
                is_alive = True if psutil.pid_exists(pid) else False
                if is_alive:
                    found_running = True
                    print(
                        f'\t{Tcolors.BOLD}* {id}{Tcolors.ENDC}:' +
                        f'{details[id]}'
                    )
                    print(f'\t\t{Tcolors.OKGREEN}is running{Tcolors.ENDC}\n')
            if not found_running:
                print(f"\t{Tcolors.BOLD}No running strategies{Tcolors.ENDC}")
        else:
            print(f"\t{Tcolors.BOLD}No running strategies{Tcolors.ENDC}")

    def abs_strategy_filepath(self, strategy_module) -> str:
        """Return absolute path to strategy file"""
        return os.path.abspath(strategy_module.__file__)

    def add_to_stm(self, strategy_details) -> bool:
        """Add new item to strategy details"""
        try:
            details = self.load_detail()
            if not details:
                details = {}
            id = strategy_details[0]
            details[id] = strategy_details[1:]
            if not self.save_detail(details):
                self.logger.error("Error in saving details")
                return False
            return True
        except Exception as err:
            self.logger.error(err)
            return False

    def remove_from_stm(self, id) -> bool:
        """Remove details of given strategy id"""
        try:
            details = self.load_detail()
            if details and id in details:
                del details[id]
                self.save_detail(details)
                return True
            else:
                self.logger.error("strategy detail id not found!")
                return False
        except Exception as err:
            self.logger.error(err)
            return False

    def save_detail(self, strategy_details) -> bool:
        """Save strategy details to file"""
        with open(self.strategy_data_filename, 'wb') as f:
            pickle.dump(strategy_details, f, pickle.HIGHEST_PROTOCOL)
            return True
        return False

    def load_detail(self) -> dict:
        """Load strategy details from file"""
        if os.path.getsize(self.strategy_data_filename) > 0:
            with open(self.strategy_data_filename, 'rb') as f:
                return pickle.load(f)
        else:
            return None

    def strategy_id_exists(self, strategy_id):
        """Check if given strategy id exists / is a running strategy"""
        details = self.load_detail()
        if details:
            if strategy_id in details.keys():
                return True
            else:
                return False
        else:
            return False

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
                id = str(uuid.uuid4())
                dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                pid = proc.pid
                strategy_details = [id, pid, strategy_name, dt]
                if self.add_to_stm(strategy_details):
                    self.logger.info(f'Strategy details saved successfully')
                else:
                    self.logger.error('Failed to add details to stm')
            except Exception as err:
                self.logger.error(err)
                return False
        return True

    def terminate(self, strategy_id) -> bool:
        """"Terminate(stop) given strategy"""
        try:
            details = self.load_detail()
            if details and details[strategy_id]:
                pid = details[strategy_id][0]
            else:
                self.logger.error("Empty strategy details")
                return False
        except Exception as err:
            self.logger.error(err)
            return False

        if not psutil.pid_exists(pid):
            self.logger.error(
                "pid does NOT exist in the system " +
                "- is the strategy running?"
            )
            return False

        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            if not self.remove_from_stm(strategy_id):
                self.logger.error("Failed to remove details from stm")
            else:
                return True
        except Exception as err:
            self.logger.error(err)
            return False
