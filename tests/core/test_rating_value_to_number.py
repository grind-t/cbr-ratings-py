from cbr_ratings._core.rating.rating_value import RATING_SCALE, rating_value_to_number


def test_converts_international_ratings(subtests):
    for number, value in enumerate(RATING_SCALE):
        with subtests.test(value=value):
            assert rating_value_to_number(value) == number


def test_converts_russian_ratings(subtests):
    for number, value in enumerate(RATING_SCALE):
        with subtests.test(value=value):
            assert rating_value_to_number(f"ru{value}") == number


def test_spot_checks_scale_ends():
    assert rating_value_to_number("AAA") == 23
    assert rating_value_to_number("ruBBB-") == 14
    assert rating_value_to_number("D") == 0


def test_returns_none_for_withdrawn_ratings(subtests):
    for value in ["Rating withdrawn", "Рейтинг отозван"]:
        with subtests.test(value=value):
            assert rating_value_to_number(value) is None
