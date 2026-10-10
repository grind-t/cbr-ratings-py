from typing import Annotated, Literal

from pydantic import BeforeValidator

from cbr_ratings._core.rating.api_values import leading_code

RatingActionCode = Literal[
    "AF", "AFP", "DG", "EWR", "NW", "NWR", "OR", "ORP", "OT", "RWR", "UP", "WD",
    "WDP", "WR",
]  # fmt: skip


def _parse_rating_actions(value: object) -> object:
    """'AF - ..., AFP - ...' -> ('AF', 'AFP')."""
    if isinstance(value, str):
        return tuple(leading_code(part) for part in value.split(", ")) if value else ()
    return value


RatingActions = Annotated[
    tuple[RatingActionCode, ...], BeforeValidator(_parse_rating_actions)
]
