from cbr_ratings._core.rating.rating_code import rating_code_to_number


def test_converts_international_ratings(subtests):
    cases = {"D": 0, "CCC": 6, "BBB-": 14, "A+": 19, "AAA": 23}
    for value, expected in cases.items():
        with subtests.test(value=value):
            assert rating_code_to_number(value) == expected


def test_russian_ratings_match_international_ones(subtests):
    for value in ["D", "BBB-", "A+", "AAA"]:
        with subtests.test(value=value):
            assert rating_code_to_number(f"ru{value}") == rating_code_to_number(value)


def test_returns_none_for_withdrawn_ratings(subtests):
    for value in ["Rating withdrawn", "Рейтинг отозван"]:
        with subtests.test(value=value):
            assert rating_code_to_number(value) is None
