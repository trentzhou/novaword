

def parse_bool(v):
    """
    Parse a bool value.

    None -> False
    False -> False
    "" -> False
    "true": -> True
    "false" -> False

    :param v: the value
    :return: bool
    """
    if not v:
        return False
    if type(v) is str or type(v) is unicode:
        if v[0] in ['T', 't', 'Y', 'y']:
            return True
        if str(v) == 'on':
            return True
    return False

def is_valid_phone_number(mobile):
    """
    Check whether a phone number is valid
    :param str mobile: phone number
    :return bool:
    """
    if mobile.isdigit() and len(mobile) == 11:
        return True
    return False
