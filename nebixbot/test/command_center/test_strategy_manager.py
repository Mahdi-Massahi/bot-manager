import unittest
from unittest.mock import patch
import os
import os.path

import nebixbot.command_center as cc
from nebixbot.command_center.strategy_manager import StrategyManager
from nebixbot.command_center.strategy.sample_strategy import sample_strategy


class TestStrategyManager(unittest.TestCase):
    """Test StrategyManager class"""

    @patch(
        'nebixbot.command_center.strategy_manager.StrategyManager',
        autospec=True
    )
    def setUp(self, sm_mock):
        self.sm = sm_mock()
        self.sm.strategy_data_filename = 'stm.dat'
        self.sm.strategies = {}

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
    def test_strategies_dict(self, strategy_mock):
        """Test strategy is in strategies dict"""
        strategy = strategy_mock("test strategy", "1.0")
        self.sm.strategies["test_strategy"] = strategy

        self.assertIn("test_strategy", self.sm.strategies)
        self.assertNotIn("not included", self.sm.strategies)

    @patch(
        "nebixbot.command_center.strategy.sample_strategy." +
        "sample_strategy.SampleStrategy",
        autospec=True,
    )
    def test_run(self, strategy_mock):
        """Test run method if strategy function is called"""
        strategy = strategy_mock("test strategy", "1.0")
        self.sm.strategies["test_strategy"] = strategy
        hasRun = self.sm.run('test_strategy')

        self.assertTrue(hasRun)

    def test_abs_strategy_filepath(self):
        """Test method returns absolute path"""
        sm = StrategyManager()
        abs_filepath = sm.abs_strategy_filepath(sample_strategy)

        self.assertIn('/sample_strategy/sample_strategy.py', abs_filepath)
        self.assertTrue(os.path.isfile(abs_filepath))

    # def test_run_strategy_module(self):
    #     """Test strategy manager runs strategy module"""
    #     sm = StrategyManager()
    #     filepath = sm.abs_strategy_filepath(sample_strategy)
