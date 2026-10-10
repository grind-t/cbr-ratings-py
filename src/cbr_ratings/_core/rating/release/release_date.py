from datetime import date, datetime
from typing import Annotated

from pydantic import BeforeValidator


def _parse_release_date(value: object) -> object:
    if isinstance(value, str):
        return datetime.strptime(value, "%d.%m.%Y").date()  # noqa: DTZ007 date only
    return value


# "DD.MM.YYYY" in the API.
ReleaseDate = Annotated[date, BeforeValidator(_parse_release_date)]
