def parse_bool(v):
    if not v:
        return False
    if type(v) is str or type(v) is unicode:
        if v[0] in ['T', 't', 'Y', 'y']:
            return True
    return False
