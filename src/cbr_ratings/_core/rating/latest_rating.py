from collections.abc import Iterable
from datetime import date
from typing import Self

from pydantic import BaseModel

from cbr_ratings._core.rating.kra import Kra
from cbr_ratings._core.rating.prediction import Prediction
from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.rating.rating_value import rating_value_to_number


class LatestRating(BaseModel):
    """A rating item reduced to what the weekly exports keep."""

    # None when the rating is withdrawn.
    value: int | None
    prediction: Prediction | None
    release_date: date

    @classmethod
    def from_item(cls, item: RatingItem) -> Self:
        return cls(
            value=_scale_number(item.rating_value),
            prediction=item.prediction,
            release_date=item.release_date,
        )


def latest_rating(items: Iterable[RatingItem]) -> RatingItem | None:
    active = [
        item
        for item in items
        if item.rating_value is not None and "WD" not in item.rating_action
    ]
    return max(active, key=_release_date) if active else None


def _scale_number(value: str | None) -> int | None:
    return None if value is None else rating_value_to_number(value)


def _release_date(item: RatingItem) -> date:
    return item.release_date


def latest_ratings_by_kra(items: Iterable[RatingItem]) -> dict[Kra, RatingItem]:
    groups: dict[Kra, list[RatingItem]] = {}
    for item in items:
        groups.setdefault(item.kra, []).append(item)

    result: dict[Kra, RatingItem] = {}
    for kra, group in groups.items():
        if (latest := latest_rating(group)) is not None:
            result[kra] = latest
    return result
