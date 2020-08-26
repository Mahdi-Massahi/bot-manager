import csv
import itertools


def validate_two_files(csvfile1, csvfile2):
    """Validates two csvfiles
    Returns:
        (are validated: bool, error: exception)
    Rules:
        1- Indexes must be the same for each row
        2- Timestamps must be the same for each row
    """

    try:
        with open(csvfile1, "r", newline="") as csv_file_1,
             open(csvfile2, "r", newline="") as csv_file_2:
            reader1 = csv.reader(csv_file_1)
            reader2 = csv.reader(csv_file_2)

            for count, (row1, row2) in enumerate(itertools.zip_longest(reader1, reader2)):
                # TODO: pass


            return True, None

    except AssertionError as err:  # failed validation
        return False, err

    except Exception:
        raise



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
                    assert(row[0] == "Index")
                    assert(row[1] == "Open")
                    assert(row[2] == "Close")
                    assert(row[3] == "High")
                    assert(row[4] == "Low")
                    assert(row[5] == "Volume")
                    assert(row[6] == "TimeStamp")
                else:  # next lines:
                    # Rule 2
                    assert(int(row[0]) == line_num)
                    # Rule 3
                    if line_num > 1:
                        assert(int(row[6]) > int(last_row[6]))
                    # Rule 4
                    for i in row[1:]:
                        assert(int(i) > 0)
                last_row = row
            # Rule 5
            assert(line_num >= 1)

            return True, None

    except AssertionError as err:  # failed validation
        return False, err

    except Exception:
        raise
