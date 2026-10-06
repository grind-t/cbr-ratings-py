import pytest

from cbr_ratings._core.rating_item import RatingItem


@pytest.fixture
def make_item():
    def make(**overrides) -> RatingItem:
        fields = {
            "rating_action": "",
            "country": "РОССИЯ",
            "ko_number": "",
            "release_date": "01.01.2000",
            "inn": "",
            "object_type": "",
            "rating_value": "BBB",
            "prediction": "",
            "object_name": "",
            "kra_name": "",
            "release_url": "",
            "object_id": "",
            "isin": "",
            "subject_name": "",
        }
        return RatingItem.model_validate(fields | overrides)

    return make
