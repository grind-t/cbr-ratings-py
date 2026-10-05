from cbr_ratings import is_rating_withdrawn


def test_true_for_withdrawn_rating_value():
    action = (
        "WD - отзыв кредитного рейтинга, WDP – отозван прогноз по кредитному рейтингу"
    )
    assert is_rating_withdrawn("Рейтинг отозван", action)


def test_handles_missing_action():
    assert is_rating_withdrawn("Рейтинг отозван")
    assert not is_rating_withdrawn("AAA")


def test_true_for_withdrawal_action():
    assert is_rating_withdrawn("", "WD")
