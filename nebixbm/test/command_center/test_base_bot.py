import unittest
import os.path

from nebixbm.log.logger import (
    delete_log_file,
    get_log_fname_path,
    get_file_name,
)
from nebixbm.command_center.bot.base_bot import BaseBot
from nebixbm.command_center.bot.sample_bot.sample_bot import (
    SampleBot,
)


class TestBaseBot(unittest.TestCase):
    """Tests for BaseBot class"""

    def test_direct_implement(self):
        """Test not to be able to use BaseBot directly"""
        with self.assertRaises(TypeError) as context:
            BaseBot("test bot", "1.0")
        self.assertIn(
            "Can't instantiate abstract class", str(context.exception)
        )

    def removed_test_implement_abstract_methods(self):
        """Test abstract methods implementation"""
        name = "test bot"
        version = "1.0"
        bot = SampleBot(name, version)
        filename = get_file_name(name, version)

        self.assertEqual("test bot", bot.name)
        self.assertEqual("1.0", bot.version)
        self.assertTrue(os.path.isfile(get_log_fname_path(filename)))
        self.assertTrue(delete_log_file(get_file_name("test bot", "1.0")))

    def removed_test__str__(self):
        """Test string format of BaseBot"""
        bot = SampleBot("test bot", "2.0.9")
        bot_str = str(bot)

        self.assertEqual(bot_str, "test_bot_2.0.9")
        self.assertTrue(delete_log_file(bot_str))
