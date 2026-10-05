import pytest

from cbr_ratings import convert_prediction


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("STA - стабильный", "STA"),
        ("STA – стабильный", "STA"),
        ("POS - позитивный", "POS"),
        ("POS – позитивный", "POS"),
        ("NEG - негативный", "NEG"),
        ("NEG – негативный", "NEG"),
        ("DEV - развивающийся", "DEV"),
        ("DEV – развивающийся", "DEV"),
    ],
)
def test_converts_known_prediction_codes(value, expected):
    assert convert_prediction(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "NA – не предусмотрен методологией",
        "UNW – неопределенный",
        "OP – иной(«рейтинг на пересмотре с возможностью понижения»)",
    ],
)
def test_returns_none_for_unsupported_or_empty_values(value):
    assert convert_prediction(value) is None
