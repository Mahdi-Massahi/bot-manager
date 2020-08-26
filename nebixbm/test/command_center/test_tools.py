import csv
import unittest
import os

from nebixbm.command_center.tools.csv_validator import csv_kline_validator


def delete_file(filename):
    """Deletes given file"""
    if os.path.isfile(filename):
        os.remove(filename)
        return True
    else:
        return False


def append_to_csvfile(csvfile, row):
    """Appends a new line to csvfile"""
    with open(csvfile, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row)


class TestValidator(unittest.TestCase):
    """Tests for csv validator"""

    def setUp(self):
        """Sets up for each test"""
        self.csvfile = "tempfile.csv"
        # TODO: create a blank csv file

    def test_line(self):
        """Tests first line's format is incorrect"""
        # TODO
        pass

    def test_index_number(self):
        """Tests index numbers are increasing by one"""
        # TODO
        pass

    def test_rows_zero(self):
        """Tests rows contain zero value"""
        # TODO
        pass

    def tearDown(self):
        """Tears down after each test"""
        self.assertTrue(delete_file(self.csvfile) == True)
