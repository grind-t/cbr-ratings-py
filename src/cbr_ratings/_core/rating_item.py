from datetime import date, datetime
from typing import Annotated

from pydantic import BeforeValidator

from cbr_ratings._core.cbr_api_model import CbrApiModel


def _parse_release_date(value: object) -> object:
    if isinstance(value, str):
        return datetime.strptime(value, "%d.%m.%Y").date()  # noqa: DTZ007 date only
    return value


class RatingItem(CbrApiModel):
    rating_action: str
    country: str
    ko_number: str
    # "DD.MM.YYYY" in the API.
    release_date: Annotated[date, BeforeValidator(_parse_release_date)]
    inn: str
    object_type: str
    rating_value: str
    prediction: str
    object_name: str
    kra_name: str
    release_url: str
    object_id: str
    isin: str
    subject_name: str
