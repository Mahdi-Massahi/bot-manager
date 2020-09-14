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
