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
