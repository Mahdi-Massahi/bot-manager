import csv
import itertools


def two_csvfile_validator(csvfile1, csvfile2):
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
                        raise Exception("csv files' indexes were not the same")
                    # Rule 2
                    if int(row1[-1]) != int(row2[-1]):
                        raise Exception(
                            "csv files' timestamps were not the same" +
                            f"{int(row1[-1])} != {int(row2[-1])}"
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
        4- All values except volume must be bigger than zero
        5- Must not be empty (more than 1 rows)
        6- TODO: number of rows must be same as the one in request

    """
    try:
        with open(csvfile, "r", newline="") as csv_file:
            is_volume_zero = False
            reader = csv.reader(csv_file)
            last_row = None
            info = None
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
                        raise ValueError("csv file first line format error")
                else:  # next lines:
                    # Rule 2
                    if int(row[0]) != line_num:
                        raise ValueError(
                            "csv file index did not match line number"
                        )
                    # Rule 3
                    if line_num > 1:
                        if int(row[6]) <= int(last_row[6]):
                            raise ValueError(
                                "csv file timestamps were not"
                                + "in an increasing order"
                            )
                    # Rule 4
                    for r in row[1:]:
                        if float(r) <= 0:
                            if float(row[5]) == 0:  # volume check
                                is_volume_zero = True
                                info = row
                            else:
                                raise ValueError(
                                    "csv file values are not bigger than 0"
                                )
                last_row = row
            # Rule 5
            if line_num < 1:
                raise ValueError("csv file lines were less than 2")
            return True, is_volume_zero, info
    except Exception as err:
        return False, err, None


def bl_validator(bl):
    """Validates wallet balance res
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        # TODO check balance res
    """
    try:
        if str(bl["ret_code"]) != '0':
            err = bl["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err


def cp_validator(cp):
    """Validates close position res
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        2- result.order_status == "Created"
        3- ignore on ret_code == 30063 : reduce only failed
        # TODO check close position res
    """
    try:
        if (str(cp["ret_code"]) != '0' and
                str(cp["ret_code"]) != '30063'):
            if cp["result"]["order_status"] != "Created":
                err = cp["ext_code"]
                raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err


def ob_validator(opd):
    """Validates orderbook
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        # TODO check orderbook
    """
    try:
        if not opd["ret_code"] == 0:
            err = opd["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err


def op_validator(op):
    """Validates open position res
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        2- result.order_status == "Created"
        3- ignore 30024 as error
    """
    try:
        if (str(op["ret_code"]) != '0' and
                str(op["ret_code"]) != '30028'):
            if op["result"]["order_status"] != "Created":
                err = op["ext_code"]
                raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err


def opd_validator(opd):
    """Validates kline csvfile
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
    """
    try:
        if not str(opd["ret_code"]) == str(0):
            err = opd["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err


def cl_validator(cl):
    """Validates change leverage
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        2- no change was needed 34015
    """
    try:
        if (str(cl["ret_code"]) != str(0) and
                str(cl["ret_code"]) != str(34015)):
            err = cl["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err
