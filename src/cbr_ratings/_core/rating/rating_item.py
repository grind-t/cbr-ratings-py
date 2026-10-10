from datetime import date
from typing import Annotated

from pydantic import BeforeValidator, Field, StringConstraints

from cbr_ratings._core.rating.action.rating_action import (
    RatingAction,
    convert_rating_action,
)
from cbr_ratings._core.rating.api_values import empty_to_none, leading_code
from cbr_ratings._core.rating.country import Country, convert_country
from cbr_ratings._core.rating.kra import Kra, convert_kra
from cbr_ratings._core.rating.object.object_type import ObjectType
from cbr_ratings._core.rating.object.security_id import SECURITY_ID_PATTERN
from cbr_ratings._core.rating.prediction import Prediction, convert_prediction
from cbr_ratings._core.rating.rating_value import convert_rating_value
from cbr_ratings._core.rating.release.release_date import convert_release_date
from cbr_ratings._core.rating.release.release_url import convert_release_url
from cbr_ratings._core.shared.cbr_api_model import CbrApiModel

_Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RatingItem(CbrApiModel):
    rating_action: Annotated[
        tuple[RatingAction, ...], BeforeValidator(convert_rating_action)
    ]
    country: Annotated[Country, BeforeValidator(convert_country)]
    # Only credit organizations have one: "1234", or "3306-ЦК" for a special license.
    ko_number: Annotated[
        Annotated[str, StringConstraints(pattern=r"^\d{4}(?:-[А-Я]{1,2})?$")] | None,
        BeforeValidator(empty_to_none),
    ]
    release_date: Annotated[date, BeforeValidator(convert_release_date)]
    # Absent for sovereign objects and some foreign issuers.
    inn: Annotated[
        Annotated[str, StringConstraints(pattern=r"^\d{10}$")] | None,
        BeforeValidator(empty_to_none),
    ]
    # The API sends "CBNK - кредитная организация".
    object_type: Annotated[ObjectType, BeforeValidator(leading_code)]
    # A RATING_SCALE value, or None when the rating is withdrawn.
    rating_value: Annotated[str | None, BeforeValidator(convert_rating_value)]
    prediction: Annotated[Prediction | None, BeforeValidator(convert_prediction)]
    object_name: _Text
    kra: Annotated[Kra, BeforeValidator(convert_kra), Field(alias="kraName")]
    release_url: Annotated[
        str,
        BeforeValidator(convert_release_url),
        StringConstraints(pattern=r"^https?://\S+$"),
    ]
    object_id: Annotated[str, StringConstraints(pattern=r"^\d+$")]
    isin: Annotated[
        Annotated[str, StringConstraints(pattern=SECURITY_ID_PATTERN)] | None,
        BeforeValidator(empty_to_none),
    ]
    # Only bonds have an issuer name.
    subject_name: Annotated[str | None, BeforeValidator(empty_to_none)]
