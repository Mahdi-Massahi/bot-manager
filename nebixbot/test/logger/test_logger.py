import unittest
import os

from nebixbot.log.logger import create_logger
from nebixbot.log.logger import delete_log_file
from nebixbot.log.logger import get_log_fname_path


class TestCreateDeleteLogger(unittest.TestCase):
    """Test creation and deletion of logger"""

    def test_create_log_file(self):
        """Test create and delete log file"""
        log_file_name = 'createlogs'
        create_logger(log_file_name, log_file_name)
        filename = get_log_fname_path(log_file_name)

        self.assertTrue(os.path.isfile(filename))
        self.assertTrue(delete_log_file(log_file_name))


class TestLogger(unittest.TestCase):
    """Test functionality of logger"""

    def setUp(self):
        """Get ready for tests"""
        log_file_name = 'testlogs'
        self.logger = create_logger(log_file_name, log_file_name)

    def test_logs_to_correct_path(self):
        """Test logger logs to correct path with correct filename"""
        message = 'this is test error'
        self.logger.error(message)

        with open(get_log_fname_path('testlogs')) as log_file:
            lines = log_file.readlines()
        was_logged = False
        for line in lines:
            if message in line:
                was_logged = True
                break
        self.assertTrue(was_logged)

    def tearDown(self):
        """Cleanup after tests"""
        delete_log_file('testlogs')
