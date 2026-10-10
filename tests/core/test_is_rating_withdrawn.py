from cbr_ratings._core.rating.action.withdrawn import is_rating_withdrawn


def test_true_for_withdrawn_rating_code():
    assert is_rating_withdrawn("Рейтинг отозван", ("WD", "WDP"))


def test_handles_missing_actions():
    assert is_rating_withdrawn("Рейтинг отозван")
    assert not is_rating_withdrawn("AAA")


def test_true_for_withdrawal_action():
    assert is_rating_withdrawn("", ("WD",))


def test_true_for_withdrawal_among_other_actions():
    assert is_rating_withdrawn("", ("DG", "WD"))


def test_false_for_withdrawn_prediction_only():
    assert not is_rating_withdrawn("BBB", ("DG", "WDP"))
