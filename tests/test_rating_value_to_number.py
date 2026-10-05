import pytest

from cbr_ratings import RATING_SCALE, rating_value_to_number


@pytest.mark.parametrize(("number", "value"), list(enumerate(RATING_SCALE)))
def test_converts_international_ratings(number, value):
    assert rating_value_to_number(value) == number


@pytest.mark.parametrize(("number", "value"), list(enumerate(RATING_SCALE)))
def test_converts_russian_ratings(number, value):
    assert rating_value_to_number(f"ru{value}") == number


def test_spot_checks_scale_ends():
    assert rating_value_to_number("AAA") == 23
    assert rating_value_to_number("ruBBB-") == 14
    assert rating_value_to_number("D") == 0


@pytest.mark.parametrize("value", ["Rating withdrawn", "Рейтинг отозван"])
def test_returns_none_for_withdrawn_ratings(value):
    assert rating_value_to_number(value) is None
