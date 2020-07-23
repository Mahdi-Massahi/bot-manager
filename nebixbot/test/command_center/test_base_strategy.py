import unittest
import os.path

from nebixbot.log.logger import (
    delete_log_file,
    get_log_fname_path,
    get_file_name,
)
from nebixbot.command_center.strategy.base_strategy import BaseStrategy
from nebixbot.command_center.strategy.sample_strategy.sample_strategy import (
    SampleStrategy,
)


class TestBaseStrategy(unittest.TestCase):
    """Tests for BaseStrategy class"""

    def test_direct_implement(self):
        """Test not to be able to use BaseStrategy directly"""
        with self.assertRaises(TypeError) as context:
            BaseStrategy('test strategy', '1.0')
        self.assertIn(
            "Can't instantiate abstract class", str(context.exception)
        )

    def test_implement_abstract_methods(self):
        """Test abstract methods implementation"""
        name = 'test strategy'
        version = '1.0'
        strategy = SampleStrategy(name, version)
        filename = get_file_name(name, version)

        self.assertEqual("test strategy", strategy.name)
        self.assertEqual("1.0", strategy.version)
        self.assertTrue(os.path.isfile(get_log_fname_path(filename)))
        self.assertEqual("before start", strategy.before_start())
        self.assertEqual("start", strategy.start())
        self.assertEqual("before termination", strategy.before_termination())
        self.assertTrue(delete_log_file(get_file_name('test strategy', '1.0')))