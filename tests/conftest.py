import pytest

from cbr_ratings._core.rating.rating_item import RatingItem


@pytest.fixture
def make_item():
    def make(**overrides) -> RatingItem:
        fields = {
            "rating_action": "AF - подтверждение кредитного рейтинга",
            "country": "РОССИЯ",
            "ko_number": "",
            "release_date": "01.01.2000",
            "inn": "",
            "object_type": "TBND - облигационный займ",
            "rating_value": "BBB",
            "prediction": "STA - стабильный",
            "object_name": "Эмитент",
            "kra": "АКРА (АО)",
            "release_url": "https://example.com",
            "object_id": "1",
            "isin": "",
            "subject_name": "",
        }
        return RatingItem.model_validate(fields | overrides)

    return make
