from typing import Annotated

from pydantic import BeforeValidator, Field, StringConstraints

from cbr_ratings._core.rating.action.rating_action import RatingActions
from cbr_ratings._core.rating.api_values import empty_to_none
from cbr_ratings._core.rating.kra import KraCode, kra_name_to_code
from cbr_ratings._core.rating.object.inn import Inn
from cbr_ratings._core.rating.object.ko_number import KoNumber
from cbr_ratings._core.rating.object.object_type import ObjectType
from cbr_ratings._core.rating.object.security_id import SecurityId
from cbr_ratings._core.rating.prediction import ItemPrediction
from cbr_ratings._core.rating.rating_value import RatingValue
from cbr_ratings._core.rating.release.release_date import ReleaseDate
from cbr_ratings._core.rating.release.release_url import ReleaseUrl
from cbr_ratings._core.search.search_form import Country
from cbr_ratings._core.shared.cbr_api_model import CbrApiModel

_Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RatingItem(CbrApiModel):
    rating_action: RatingActions
    country: Country
    ko_number: KoNumber
    release_date: ReleaseDate
    inn: Inn
    object_type: ObjectType
    # A RATING_SCALE value, or None when the rating is withdrawn.
    rating_value: RatingValue
    prediction: ItemPrediction
    object_name: _Text
    kra_code: Annotated[
        KraCode, BeforeValidator(kra_name_to_code), Field(alias="kraName")
    ]
    release_url: ReleaseUrl
    object_id: Annotated[str, StringConstraints(pattern=r"^\d+$")]
    isin: SecurityId
    # Only bonds have an issuer name.
    subject_name: Annotated[str | None, BeforeValidator(empty_to_none)]
