from cbr_ratings._core.rating.withdrawn import is_rating_withdrawn


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


def test_true_for_withdrawal_among_other_actions():
    action = "DG - Понижение кредитного рейтинга, WD - Отзыв кредитного рейтинга"
    assert is_rating_withdrawn("", action)


def test_false_for_withdrawn_prediction_only():
    action = "DG – понижение кредитного рейтинга, WDP – отзыв прогноза"
    assert not is_rating_withdrawn("BBB", action)
