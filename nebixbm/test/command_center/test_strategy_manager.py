import unittest
from unittest.mock import patch
import os
import os.path

import nebixbm.command_center as cc
from nebixbm.command_center.bot_manager import BotManager
from nebixbm.command_center.bot.sample_bot import sample_bot
from nebixbm.log.logger import delete_log_file


class TestBotManager(unittest.TestCase):
    """Test BotManager class"""

    @patch(
        "nebixbm.command_center.bot_manager.BotManager",
        autospec=True,
    )
    def setUp(self, sm_mock):
        self.sm = sm_mock()
        self.sm.bot_data_filename = "stm.dat"
        self.sm.bots = {}
        self.sm_real = BotManager()
        self.logger_filename = "bot_manager"

    def test_bots_data_file_exists(self):
        """Test if bots_data file exists"""
        path = os.path.abspath(cc.__file__.replace("__init__.py", ""))
        filepath = os.path.join(path, self.sm.bot_data_filename)

        self.assertTrue(os.path.isfile(filepath))

    @patch(
        "nebixbm.command_center.bot.sample_bot."
        + "sample_bot.SampleBot",
        autospec=True,
    )
    def test_bots_dict(self, bot_mock):
        """Test bot is in bots dict"""
        bot = bot_mock("test bot", "1.0")
        self.sm.bots["test_bot"] = bot

        self.assertIn("test_bot", self.sm.bots)
        self.assertNotIn("not included", self.sm.bots)

    @patch(
        "nebixbm.command_center.bot.sample_bot."
        + "sample_bot.SampleBot",
        autospec=True,
    )
    def test_run(self, bot_mock):
        """Test run method if bot function is called"""
        bot = bot_mock("test bot", "1.0")
        self.sm.bots["test_bot"] = bot
        hasRun = self.sm.run("test_bot")

        self.assertTrue(hasRun)

    def test_abs_bot_filepath(self):
        """Test method returns absolute path"""
        abs_filepath = self.sm_real.abs_bot_filepath(sample_bot)

        self.assertIn("/sample_bot/sample_bot.py", abs_filepath)
        self.assertTrue(os.path.isfile(abs_filepath))
        self.assertTrue(delete_log_file(self.logger_filename))

    def removed_test_add_to_stm_input(self):
        """Test input of add to stm method"""
        bot_details = None
        bot_details2 = ["test", "test", "test"]

        self.assertFalse(self.sm_real.add_to_stm(bot_details))
        self.assertFalse(self.sm_real.add_to_stm(bot_details2))
