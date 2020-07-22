import unittest
from unittest.mock import patch
import os
import os.path

import nebixbot.command_center as cc
from nebixbot.command_center.strategy_manager import StrategyManager


class TestStrategyManager(unittest.TestCase):
    """Test StrategyManager class"""

    def setUp(self):
        self.sm = StrategyManager()

    def test_strategies_data_file_exists(self):
        """Test if strategies_data file exists"""
        path = os.path.abspath(cc.__file__.replace("__init__.py", ""))
        filepath = os.path.join(path, self.sm.strategy_data_filename)

        self.assertTrue(os.path.isfile(filepath))

    @patch(
        "nebixbot.command_center.strategy.sample_strategy." +
        "sample_strategy.SampleStrategy",
        autospec=True,
    )
    def test_run_strategy_name(self, strategy_mock):
        """Test strategy_name for run method"""
        strategy = strategy_mock("test strategy", "1.0")
        self.sm.strategies["test_strategy"] = strategy

        self.assertTrue(self.sm.run("test_strategy"))
        self.assertFalse(self.sm.run("not included strategy"))

    @patch(
        "nebixbot.command_center.strategy.sample_strategy." +
        "sample_strategy.SampleStrategy",
        autospec=True,
    )
    def test_run(self, strategy_mock):
        """Test run method if strategy functions are called"""
        strategy = strategy_mock("test strategy", "1.0")
        self.sm.strategies["test_strategy"] = strategy
        self.sm.run('test_strategy')

        self.assertTrue(strategy.before_start.called)
        self.assertTrue(strategy.start.called)
        self.assertFalse(strategy.before_termination.called)
