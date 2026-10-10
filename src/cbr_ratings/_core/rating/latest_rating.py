from collections.abc import Iterable
from datetime import date
from typing import Self

from pydantic import BaseModel

from cbr_ratings._core.rating.action.withdrawn import is_rating_withdrawn
from cbr_ratings._core.rating.kra import Kra, convert_kra_name
from cbr_ratings._core.rating.prediction import Prediction, convert_prediction
from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.rating.rating_value import rating_value_to_number


class LatestRating(BaseModel):
    """A rating item reduced to what the weekly exports keep."""

    # None when the value is not on RATING_SCALE.
    value: int | None
    prediction: Prediction | None
    release_date: date

    @classmethod
    def from_item(cls, item: RatingItem) -> Self:
        return cls(
            value=rating_value_to_number(item.rating_value),
            prediction=convert_prediction(item.prediction),
            release_date=item.release_date,
        )


def latest_rating(items: Iterable[RatingItem]) -> RatingItem | None:
    active = [
        item
        for item in items
        if not is_rating_withdrawn(item.rating_value, item.rating_action)
    ]
    return max(active, key=_release_date) if active else None


def _release_date(item: RatingItem) -> date:
    return item.release_date


def latest_ratings_by_kra(items: Iterable[RatingItem]) -> dict[Kra, RatingItem]:
    groups: dict[Kra, list[RatingItem]] = {}
    for item in items:
        groups.setdefault(convert_kra_name(item.kra_name), []).append(item)

    result: dict[Kra, RatingItem] = {}
    for kra, group in groups.items():
        if (latest := latest_rating(group)) is not None:
            result[kra] = latest
    return result
