from datetime import datetime


def convert_release_date(value: object) -> object:
    """'DD.MM.YYYY' -> date."""
    if isinstance(value, str):
        return datetime.strptime(value, "%d.%m.%Y").date()  # noqa: DTZ007 date only
    return value
