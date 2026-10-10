import pytest

from cbr_ratings._core.rating.prediction import convert_prediction


def test_converts_known_prediction_codes(subtests):
    cases = {
        "STA - стабильный": "STA",
        "STA – стабильный": "STA",
        "POS - позитивный": "POS",
        "POS – позитивный": "POS",
        "NEG - негативный": "NEG",
        "NEG – негативный": "NEG",
        "DEV - развивающийся": "DEV",
        "DEV – развивающийся": "DEV",
    }
    for value, expected in cases.items():
        with subtests.test(value=value):
            assert convert_prediction(value) == expected


def test_returns_none_for_unsupported_or_empty_values(subtests):
    values = [
        None,
        "",
        "NA – не предусмотрен методологией",
        "UNW – неопределенный",
        "OP – иной(«рейтинг на пересмотре с возможностью понижения»)",
    ]
    for value in values:
        with subtests.test(value=value):
            assert convert_prediction(value) is None


def test_rejects_unknown_prediction_codes():
    with pytest.raises(ValueError, match="unknown prediction"):
        convert_prediction("ZZ - неизвестный")
