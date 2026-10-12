import re
from datetime import date, datetime

# the registry sends DD.MM.YYYY, a dumped RatingItem holds YYYY-MM-DD
_FORMATS = {
    re.compile(r"\d{2}\.\d{2}\.\d{4}"): "%d.%m.%Y",
    re.compile(r"\d{4}-\d{2}-\d{2}"): "%Y-%m-%d",
}


def convert_release_date(value: object) -> date:
    """'DD.MM.YYYY' (registry) or 'YYYY-MM-DD' (dump) -> date; nothing else."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for pattern, date_format in _FORMATS.items():
            if pattern.fullmatch(value):
                return datetime.strptime(value, date_format).date()  # noqa: DTZ007 date only
    raise ValueError(f"unknown release date: {value!r}")
