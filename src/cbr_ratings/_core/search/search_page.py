from collections.abc import Mapping
from typing import Any, Self

from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.shared.cbr_api_model import CbrApiModel

_NOT_FOUND_ERROR = {"message": "Array", "code": 0, "customData": None}


class RatingSearchPage(CbrApiModel):
    page_count: int
    page_number: int
    sorting_field: str
    sorting_direction: str
    page_size: int
    item_list: list[RatingItem]
    item_count: int

    @classmethod
    def from_response(cls, body: Mapping[str, Any]) -> Self | None:
        """Return None when nothing is found."""
        # The site reports an empty result as this error.
        if body["status"] == "error" and body["errors"] == [_NOT_FOUND_ERROR]:
            return None

        if body["status"] != "success":
            raise CbrRatingsError(body["errors"])

        return cls.model_validate(body["data"])
