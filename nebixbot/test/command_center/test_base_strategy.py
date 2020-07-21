import unittest

from nebixbot.log.logger import delete_log_file
from nebixbot.command_center.strategy.base_strategy import BaseStrategy
from nebixbot.command_center.strategy.sample_strategy.sample_strategy import (
    SampleStrategy,
)


class TestBaseStrategy(unittest.TestCase):
    """Tests for BaseStrategy class"""

    def test_direct_implement(self):
        """Test not to be able to use BaseStrategy directly"""
        with self.assertRaises(TypeError) as context:
            BaseStrategy()
        self.assertIn(
            "Can't instantiate abstract class", str(context.exception)
        )

    def test_implement_abstract_methods(self):
        """Test abstract methods implementation"""
        strategy = SampleStrategy("test strategy", "1.0")

        self.assertEqual("test strategy", strategy.name)
        self.assertEqual("1.0", strategy.version)
        self.assertEqual("before start", strategy.before_start())
        self.assertEqual("start", strategy.start())
        self.assertEqual("before termination", strategy.before_termination())

    def tearDown(self):
        delete_log_file("test strategy")
