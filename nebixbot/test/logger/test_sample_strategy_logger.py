import unittest

from nebixbot.log.logger import get_log_fname_path, delete_log_file
from nebixbot.command_center.strategy.sample_strategy.sample_strategy import (
    SampleStrategy,
)


class TestSampleStrategyLogger(unittest.TestCase):
    """Test logger for SampleStrategy class"""

    def setUp(self):
        name = 'sample strategy'
        version = '0.0.1'
        self.sample_strategy = SampleStrategy(name, version)
        self.logger_filename = f'{self.sample_strategy.name}_{self.sample_strategy.version}'

    def test_before_start_log(self):
        """Test logs before start"""
        self.sample_strategy.before_start()

        message = "it's before start"
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
        self.sample_strategy.start()

        message = "it's start"
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
        self.sample_strategy.before_termination()

        message = "it's before termination"
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
