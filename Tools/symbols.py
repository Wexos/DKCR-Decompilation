def is_anonymous_data_symbol(symbol):
    if not symbol.startswith("@"):
        return False

    if symbol.startswith("@STRING@"):
        return True

    for c in symbol[1:]:
        if c < '0' or c > '9':
            return False

    return True