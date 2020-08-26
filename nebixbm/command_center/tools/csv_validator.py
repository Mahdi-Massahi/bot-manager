import csv


def csv_kline_validator(csvfile, timestamp_delta):
    """Validates kline csvfile
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- 1st line format: "Index, Open, Close, High, Low, Volume, TimeStamp"
        2- Index must start from 1 and increase by one
        3- TimeStamp must increase by a fixed delta
        4- All values must be bigger than zero
        5- Must not be empty and have more than 2 rows
    """

    try:
        with open(csvfile, "r", newline="") as csv_file:
            reader = csv.reader(csvfile)

            # TODO: Rule 5

            for line in reader:  # TODO: check this syntax
                items = line.split(",")

                # TODO: if first line check strings:

                # Rule 1
                assert(items[0] == "Index")
                assert(items[1] == "Open")
                assert(items[2] == "Close")
                assert(items[3] == "High")
                assert(items[4] == "Low")
                assert(items[5] == "Volume")
                assert(items[6] == "TimeStamp")

                # TODO: if next lines:

                # Rule 2
                assert(int(items[0]) == linenumber)

                # Rule 3
                # TODO: Check TimeStamp delta

                # Rule 4
                for i in items[1:]:
                    assert(float(items[i]) > 0)

        return True, None

    except AssertionError as err:  # failed validation
        return False, err

    except Exception as err:  # TODO: IOException?
        raise
