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
