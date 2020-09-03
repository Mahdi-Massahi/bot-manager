import csv
import unittest
import os

from nebixbm.command_center.tools.csv_validator import (
    csv_kline_validator,
    validate_two_csvfiles,
)


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
        self.second_csvfile = "second_csvfile.csv"
        with open(self.csvfile, "w"), open(self.second_csvfile, "w"):
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

    def test_volume_zero(self):
        """Tests volume contains zero value"""
        append_to_csvfile(
            self.csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.csvfile,
            ["1", "100", "100", "100", "100", "0", "100"]
        )
        res, volume_zero_state = csv_kline_validator(self.csvfile)

        self.assertTrue(res)

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

    def test_two_correct_csv(self):
        """Test index of two csv files are the same in each row"""
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
            ["2", "100", "100", "100", "100", "100", "120"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["1", "100", "100", "100", "100", "100", "100"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["2", "100", "100", "100", "100", "100", "120"]
        )
        res1, _ = csv_kline_validator(self.csvfile)
        res2, _ = csv_kline_validator(self.second_csvfile)
        res3, _ = validate_two_csvfiles(self.csvfile, self.second_csvfile)

        self.assertTrue(res1)
        self.assertTrue(res2)
        self.assertTrue(res3)

    def test_two_incorrect_csv_index(self):
        """Test index of two csv files are the same in each row"""
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
            ["2", "100", "100", "100", "100", "100", "120"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["1", "100", "100", "100", "100", "100", "100"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["3", "100", "100", "100", "100", "100", "120"]
        )
        res1, _ = csv_kline_validator(self.csvfile)
        res2, _ = csv_kline_validator(self.second_csvfile)
        res3, _ = validate_two_csvfiles(self.csvfile, self.second_csvfile)

        self.assertTrue(res1)
        self.assertFalse(res2)
        self.assertFalse(res3)

    def test_two_incorrect_csv_timestamps(self):
        """Test index of two csv files are the same in each row"""
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
            ["2", "100", "100", "100", "100", "100", "120"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["Index", "Open", "Close", "High", "Low", "Volume", "TimeStamp"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["1", "100", "100", "100", "100", "100", "100"]
        )
        append_to_csvfile(
            self.second_csvfile,
            ["2", "100", "100", "100", "100", "100", "190"]
        )
        res1, _ = csv_kline_validator(self.csvfile)
        res2, _ = csv_kline_validator(self.second_csvfile)
        res3, _ = validate_two_csvfiles(self.csvfile, self.second_csvfile)

        self.assertTrue(res1)
        self.assertTrue(res2)
        self.assertFalse(res3)

    def tearDown(self):
        """Tears down after each test"""
        self.assertTrue(delete_file(self.csvfile))
        self.assertTrue(delete_file(self.second_csvfile))
