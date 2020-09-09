def opd_validator(opd):
    """Validates kline csvfile
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
    """
    try:
        if not opd["ret_code"] == 0:
            err = opd["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err
