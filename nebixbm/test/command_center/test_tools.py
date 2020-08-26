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


def append_to_csvfile(csvfile, row: list):
    """Appends a new line to csvfile"""
    with open(csvfile, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row)


class TestValidator(unittest.TestCase):
    """Tests for csv validator"""

    def setUp(self):
        """Sets up for each test"""
        self.csvfile = "tempfile.csv"
        with open(self.csvfile, "w"):
            pass

    def test_first_line(self):
        """Tests first line's format is incorrect"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["1", "100", "100", "100", "100", "100", "100"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertTrue(res)

    def test_empty_csv(self):
        """Test if csv is empty or has less than 2 lines"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertFalse(res)

    def test_index_number(self):
        """Tests index numbers are increasing by one"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["1", "100", "100", "100", "100", "100", "100"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertTrue(res)

    def test_index_number2(self):
        """Test index must start from 1"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["2", "100", "100", "100", "100", "100", "100"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertFalse(res)

    def test_index_increase(self):
        """Test index must start from 1 and increase by one"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["1", "100", "100", "100", "100", "100", "100"]
        )
        append_to_csvfile(
            self.csvfile,
            ["3", "100", "100", "100", "100", "100", "100"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertFalse(res)

    def test_rows_zero(self):
        """Tests rows contain zero value"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["1", "100", "0", "100", "100", "100", "100"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertFalse(res)

    def test_timestamp_increases(self):
        """Test TimeStamp icreases in each row"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["1", "1", "1", "1", "1", "1", "1000"]
        )
        append_to_csvfile(
            self.csvfile,
            ["2", "2", "2", "2", "2", "2", "500"]
        )
        res, _ = csv_kline_validator(self.csvfile)

        self.assertFalse(res)

    def tearDown(self):
        """Tears down after each test"""
        self.assertTrue(delete_file(self.csvfile))
