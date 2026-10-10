_NO_VALUE = ("", "-")


def empty_to_none(value: object) -> object:
    """The API sends "" or "-" for a missing value."""
    return None if isinstance(value, str) and value.strip() in _NO_VALUE else value


def leading_code(value: object) -> object:
    """'TBND - bond' -> 'TBND': the code before the dash in "CODE - text"."""
    if isinstance(value, str):
        return value.split(maxsplit=1)[0] if value.strip() else None
    return value
