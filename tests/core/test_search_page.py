import pytest

from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.search.search_page import RatingSearchPage


def test_not_found_error_means_no_page():
    body = {
        "status": "error",
        "errors": [{"message": "Array", "code": 0, "customData": None}],
    }

    assert RatingSearchPage.from_response(body) is None


def test_other_errors_are_raised():
    body = {"status": "error", "errors": [{"message": "boom", "code": 1}]}

    with pytest.raises(CbrRatingsError):
        RatingSearchPage.from_response(body)
