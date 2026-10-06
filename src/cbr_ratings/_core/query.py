from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from cbr_ratings._core.search_form import (
    Country,
    KraName,
    RatingAction,
    RatingGroup,
    RatingScale,
    RatingStatus,
    TypeGroup,
)


@dataclass(frozen=True, kw_only=True)
class RatingQuery:
    """Filters of the advanced search form on ratings.cbr.ru."""

    date_from: date | None = None
    date_to: date | None = None
    rating_name: str | None = None
    inn: str | None = None
    isin: str | None = None
    ko_number: str | None = None
    country: Sequence[Country] | None = None
    type_group: Sequence[TypeGroup] | None = None
    kra_name: Sequence[KraName] | None = None
    rating_scale: Sequence[RatingScale] | None = None
    rating_group: Sequence[RatingGroup] | None = None
    rating_action: Sequence[RatingAction] | None = None
    rating_status: Sequence[RatingStatus] | None = None
