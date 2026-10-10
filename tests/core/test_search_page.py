import pytest

from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.search.search_page import RatingSearchPage


def test_other_errors_are_raised():
    body = {"status": "error", "errors": [{"message": "boom", "code": 1}]}

    with pytest.raises(CbrRatingsError):
        RatingSearchPage.from_response(body)
