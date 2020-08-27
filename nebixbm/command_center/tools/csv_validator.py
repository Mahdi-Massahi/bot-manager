import csv
import itertools


def validate_two_csvfiles(csvfile1, csvfile2):
    """Validates two csvfiles
    Returns:
        (are validated: bool, error: exception)
    Rules:
        1- Indexes must be the same for each row
        2- Timestamps must be the same for each row
    """
    try:
        with open(csvfile1, "r", newline="") as csv_file_1, open(
            csvfile2, "r", newline=""
        ) as csv_file_2:
            reader1 = csv.reader(csv_file_1)
            reader2 = csv.reader(csv_file_2)
            for count, (row1, row2) in enumerate(
                itertools.zip_longest(reader1, reader2)
            ):
                if count > 0:
                    # Rule 1
                    if int(row1[0]) != int(row2[0]):
                        raise Exception("csvfiles' indexes were not the same")
                    # Rule 2
                    if int(row1[-1]) != int(row2[-1]):
                        raise Exception(
                            "csvfiles' timestamps were not the same"
                        )
            return True, None
    except Exception as err:
        return False, err


def csv_kline_validator(csvfile):
    """Validates kline csvfile
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- 1st line format: "Index, Open, Close, High, Low, Volume, TimeStamp"
        2- Index must start from 1 and increase by one
        3- TimeStamp must increase by a fixed delta
        4- All values must be bigger than zero
        5- Must not be empty (more than 1 rows)
    """
    try:
        with open(csvfile, "r", newline="") as csv_file:
            reader = csv.reader(csv_file)
            last_row = None
            for count, row in enumerate(reader):
                line_num = count
                if line_num == 0:
                    # Rule 1
                    if (
                        row[0] != "Index"
                        or row[1] != "Open"
                        or row[2] != "Close"
                        or row[3] != "High"
                        or row[4] != "Low"
                        or row[5] != "Volume"
                        or row[6] != "TimeStamp"
                    ):
                        raise ValueError("csvfile first line format error")
                else:  # next lines:
                    # Rule 2
                    if int(row[0]) != line_num:
                        raise ValueError(
                            "csvfile index did not match line number"
                        )
                    # Rule 3
                    if line_num > 1:
                        if int(row[6]) <= int(last_row[6]):
                            raise ValueError(
                                "csvfile timestamps were not"
                                + "in an increasing order"
                            )
                    # Rule 4
                    for i in row[1:]:
                        if int(i) <= 0:
                            raise ValueError(
                                "csvfile values are not bigger than 0"
                            )
                last_row = row
            # Rule 5
            if line_num < 1:
                raise ValueError("csvfile lines were less than 2")
            return True, None
    except Exception as err:
        return False, err