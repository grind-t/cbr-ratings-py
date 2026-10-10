import re
from typing import Literal, get_args

from cbr_ratings._core.rating.action.withdrawn import is_rating_withdrawn

RatingValue = Literal[
    "D", "C", "CC-", "CC", "CC+", "CCC-", "CCC", "CCC+", "B-", "B", "B+", "BB-",
    "BB", "BB+", "BBB-", "BBB", "BBB+", "A-", "A", "A+", "AA-", "AA", "AA+", "AAA",
]  # fmt: skip

RATING_SCALE = get_args(RatingValue)

_RATING_RE = re.compile(r"[A-D]{1,3}[+-]?", re.IGNORECASE)


def rating_value_to_number(
    value: str, scale: tuple[str, ...] = RATING_SCALE
) -> int | None:
    match = _RATING_RE.search(value)
    if match is None or match[0] not in scale:
        return None
    return scale.index(match[0])


def convert_rating_value(value: str) -> RatingValue | None:
    """Strip the agency notation ("ruAA-", "AA(RU)") down to a RATING_SCALE value.

    A withdrawn rating becomes None; any other value off the scale is an error.
    """
    if is_rating_withdrawn(value.strip()):
        return None
    match = _RATING_RE.search(value)
    for rating_value in RATING_SCALE:
        if match is not None and match[0] == rating_value:
            return rating_value
    raise ValueError(f"unknown rating value: {value!r}")
