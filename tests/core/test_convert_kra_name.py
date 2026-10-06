import pytest

from cbr_ratings._core.kra import convert_kra_name


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ('АО "Эксперт РА"', "EXPERT_RA"),
        ("АКРА (АО)", "AKRA"),
        ('ООО "НКР"', "NKR"),
        ('ООО "НРА"', "NRA"),
        ("Unknown", "UNKNOWN"),
    ],
)
def test_converts_kra_name(value, expected):
    assert convert_kra_name(value) == expected
