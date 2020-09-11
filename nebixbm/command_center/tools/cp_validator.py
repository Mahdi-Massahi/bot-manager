def cp_validator(cp):
    """Validates close position res
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        2- result.order_status == "Created"
        # TODO check close position res
    """
    try:
        if (not cp["ret_code"] == 0 or
                not cp["result"]["order_status"] == "Created"):
            err = cp["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err
