def cp_validator(opd):
    """Validates close position res
    Returns:
        (is validated: bool, error: exception)
    Rules:
        1- ret_code == 0
        # TODO check close position res
    """
    try:
        if not opd["ret_code"] == 0:
            err = opd["ext_code"]
            raise Exception(f"exit code: {err}")
        else:
            return True, None
    except Exception as err:
        return False, err
