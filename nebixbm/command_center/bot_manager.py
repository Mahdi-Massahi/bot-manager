import os
import signal
import subprocess
import psutil
import uuid
import pickle
from datetime import datetime
import time

from nebixbm.log.logger import create_logger
from nebixbm.command_center.bot.available_bots import (
    get_available_bots,
)


class BotManager:
    """The bot control unit"""

    def __init__(self):
        self.CLEAN_UP_TIME = 10
        head, _ = os.path.split(os.path.abspath(__file__))
        self.bot_data_filename = os.path.join(head, "stm.dat")
        self.logger, self.log_filepath = create_logger(
            "bot_manager", "bot_manager"
        )
        self.bots = get_available_bots()

    def log_logfile_path(self):
        """Log logfile path into logger"""
        self.logger.info(f"Logger: {self.log_filepath}")

    def return_available_bots(self) -> dict:
        """Return available bots (to run)"""
        result = {}
        for bot_name in self.bots.keys():
            result[bot_name] = self.bots[bot_name].__name__

        return result

    def return_running_bots(self) -> dict:
        """Return list of running and dead bots"""
        running = []
        dead = []
        details = self.load_detail()
        if details:
            for id in details.keys():
                pid = details[id][0]
                is_alive = True if psutil.pid_exists(pid) else False
                if is_alive:
                    running.append([id, details[id]])
                else:
                    dead.append([id, details[id]])

        return running, dead

    def abs_bot_filepath(self, bot_module) -> str:
        """Return absolute path to bot file"""
        return os.path.abspath(bot_module.__file__)

    def add_to_stm(self, bot_details) -> bool:
        """Add new item to bot details"""
        if not bot_details:
            self.logger.error(
                "Empty bot details can not be added to stm"
            )
            return False
        if len(bot_details) != 4:
            self.logger.error(
                "Bot details format error" + " - few arguements?"
            )
            return False
        try:
            details = self.load_detail()
            if not details:
                details = {}
            id = bot_details[0]
            details[id] = bot_details[1:]
            if not self.save_detail(details):
                self.logger.error("Error in saving details")
                return False
            return True
        except Exception as err:
            self.logger.error(err)
            return False

    def remove_from_stm(self, id) -> bool:
        """Remove details of given bot id"""
        try:
            details = self.load_detail()
            if details and id in details:
                del details[id]
                self.save_detail(details)
                return True
            else:
                self.logger.error("bot detail id not found!")
                return False
        except Exception as err:
            self.logger.error(err)
            return False

    def save_detail(self, bot_details) -> bool:
        """Save bot details to file"""
        with open(self.bot_data_filename, "wb") as f:
            pickle.dump(bot_details, f, pickle.HIGHEST_PROTOCOL)
            return True
        return False

    def load_detail(self) -> dict:
        """Load bot details from file"""
        if os.path.getsize(self.bot_data_filename) > 0:
            with open(self.bot_data_filename, "rb") as f:
                return pickle.load(f)
        else:
            return None

    def bot_id_exists(self, bot_id):
        """Check if given bot id exists"""
        details = self.load_detail()
        if details:
            if bot_id in details.keys():
                return True
            else:
                return False
        else:
            return False

    def run(self, bot_name) -> bool:
        """Run(start) given bot"""
        if bot_name not in self.bots:
            return False
        else:
            bot = self.bots[bot_name]
            filepath = self.abs_bot_filepath(bot)
            try:
                proc = subprocess.Popen(
                    f"python3 {filepath}", shell=True, preexec_fn=os.setsid
                )
                id = str(uuid.uuid4())
                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pid = proc.pid
                bot_details = [id, pid, bot_name, dt]
                if self.add_to_stm(bot_details):
                    self.logger.info(
                        "Successfully saved bot details:"
                        + f"{bot_details}"
                    )
                else:
                    self.logger.error("Failed to add details to stm")
            except Exception as err:
                self.logger.error(err)
                return False
        return True

    def terminate(self, bot_id) -> bool:
        """"Terminate(stop) given bot"""
        try:
            details = self.load_detail()
            if details and details[bot_id]:
                pid = details[bot_id][0]
            else:
                self.logger.error("Empty bot details")
                return False
        except Exception as err:
            self.logger.error(err)
            return False

        if not psutil.pid_exists(pid):
            self.logger.error(
                "pid does NOT exist in the system "
                + "- is the bot running?"
            )
            return False

        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            self.logger.info(f"Sent SIGTERM to pid={pid}")
            self.logger.info(
                f"Waiting {self.CLEAN_UP_TIME} seconds"
                + " to let the subprocess clean up"
            )
            time.sleep(self.CLEAN_UP_TIME)

            if psutil.pid_exists(pid):
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                self.logger.info(
                    "Subprocess was not terminated, "
                    + f"sent another SIGTERM to pid={pid}"
                )

            # if not self.remove_from_stm(bot_id):
            #     self.logger.error("Failed to remove details from stm")

            else:
                self.logger.info(
                    "Successfully terminated " + f"subprocess (pid={pid})"
                )
                return True
        except Exception as err:
            self.logger.error(err)
            return False
