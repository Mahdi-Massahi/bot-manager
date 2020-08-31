import unittest

from nebixbm.log.logger import get_log_fname_path, delete_log_file
from nebixbm.command_center.bot.sample_bot.sample_bot import SampleBot


class TestSampleBotLogger(unittest.TestCase):
    """Test logger for SampleBot class"""

    def setUp(self):
        name = "sample bot"
        version = "0.0.1"
        self.sample_bot = SampleBot(name, version)
        self.logger_filename = str(self.sample_bot)

    def test_before_start_log(self):
        """Test logs before start"""
        self.sample_bot.before_start()

        message = "test before start"
        with open(get_log_fname_path(self.logger_filename)) as log_file:
            lines = log_file.readlines()
        was_logged = False
        for line in lines:
            if message in line:
                was_logged = True
                break

        self.assertTrue(was_logged)

    def test_start_log(self):
        """Test logs start"""
        self.sample_bot.start()

        message = "test start"
        with open(get_log_fname_path(self.logger_filename)) as log_file:
            lines = log_file.readlines()
        was_logged = False
        for line in lines:
            if message in line:
                was_logged = True
                break

        self.assertTrue(was_logged)

    def test_before_termination(self):
        """Test logs before terminating"""
        self.sample_bot.before_termination()

        message = "test before termination"
        with open(get_log_fname_path(self.logger_filename)) as log_file:
            lines = log_file.readlines()
        was_logged = False
        for line in lines:
            if message in line:
                was_logged = True
                break

        self.assertTrue(was_logged)

    def tearDown(self):
        self.assertTrue(delete_log_file(self.logger_filename))
