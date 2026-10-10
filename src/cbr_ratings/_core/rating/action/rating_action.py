from typing import Literal

from cbr_ratings._core.rating.api_values import leading_code

RatingAction = Literal[
    "AF", "AFP", "DG", "EWR", "NW", "NWR", "OR", "ORP", "OT", "RWR", "UP", "WD",
    "WDP", "WR",
]  # fmt: skip


def convert_rating_action(value: object) -> object:
    """'AF - ..., AFP - ...' -> ('AF', 'AFP')."""
    if isinstance(value, str):
        return tuple(leading_code(part) for part in value.split(", ")) if value else ()
    return value
