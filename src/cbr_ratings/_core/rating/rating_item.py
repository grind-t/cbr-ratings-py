from datetime import date
from typing import Annotated

from pydantic import BeforeValidator, Field, StringConstraints, computed_field

from cbr_ratings._core.rating.action.rating_action import (
    RatingAction,
    convert_rating_action,
)
from cbr_ratings._core.rating.api_values import empty_to_none, leading_code
from cbr_ratings._core.rating.country import Country, convert_country
from cbr_ratings._core.rating.kra import KraCode, convert_kra_name
from cbr_ratings._core.rating.object.object_type import ObjectType
from cbr_ratings._core.rating.object.security_id import SECURITY_ID_PATTERN
from cbr_ratings._core.rating.prediction import Prediction, convert_prediction
from cbr_ratings._core.rating.rating_code import (
    RatingCode,
    convert_rating_code,
    rating_code_to_number,
)
from cbr_ratings._core.rating.release.release_date import convert_release_date
from cbr_ratings._core.rating.release.release_url import convert_release_url
from cbr_ratings._core.shared.cbr_api_model import CbrApiModel

_Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RatingItem(CbrApiModel):
    rating_action: Annotated[
        tuple[RatingAction, ...], BeforeValidator(convert_rating_action)
    ]
    country: Annotated[Country, BeforeValidator(convert_country)]
    ko_number: Annotated[
        Annotated[str, StringConstraints(pattern=r"^\d{4}(?:-[А-Я]{1,2})?$")] | None,
        BeforeValidator(empty_to_none),
    ]
    release_date: Annotated[date, BeforeValidator(convert_release_date)]
    inn: Annotated[
        Annotated[str, StringConstraints(pattern=r"^\d{10}$")] | None,
        BeforeValidator(empty_to_none),
    ]
    object_type: Annotated[ObjectType, BeforeValidator(leading_code)]
    rating_code: Annotated[
        RatingCode | None,
        BeforeValidator(convert_rating_code),
        Field(alias="ratingValue"),
    ]
    prediction: Annotated[Prediction | None, BeforeValidator(convert_prediction)]
    object_name: _Text
    kra_code: Annotated[
        KraCode, BeforeValidator(convert_kra_name), Field(alias="kraName")
    ]
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
    subject_name: Annotated[str | None, BeforeValidator(empty_to_none)]

    @computed_field
    @property
    def rating_number(self) -> int | None:
        if self.rating_code is None:
            return None
        return rating_code_to_number(self.rating_code)
