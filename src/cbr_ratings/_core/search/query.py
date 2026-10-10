from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from cbr_ratings._core.search.search_form import (
    SearchFormCountry,
    SearchFormKraName,
    SearchFormRatingAction,
    SearchFormRatingGroup,
    SearchFormRatingScale,
    SearchFormRatingStatus,
    SearchFormTypeGroup,
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
    country: Sequence[SearchFormCountry] | None = None
    type_group: Sequence[SearchFormTypeGroup] | None = None
    kra_name: Sequence[SearchFormKraName] | None = None
    rating_scale: Sequence[SearchFormRatingScale] | None = None
    rating_group: Sequence[SearchFormRatingGroup] | None = None
    rating_action: Sequence[SearchFormRatingAction] | None = None
    rating_status: Sequence[SearchFormRatingStatus] | None = None
