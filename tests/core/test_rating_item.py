import pytest
from pydantic import ValidationError


def test_keeps_codes_of_code_and_text_fields(make_item):
    item = make_item(
        rating_action="DG – понижение кредитного рейтинга, OT – изменение прогноза",
        object_type="CBNK – кредитная организация",
        prediction="NEG - негативный",
    )

    assert item.rating_action == ("DG", "OT")
    assert item.object_type == "CBNK"
    assert item.prediction == "NEG"


def test_normalizes_rating_value_to_the_scale_form(make_item, subtests):
    for raw, expected in {
        "ruAA-": "AA-",
        "AA(RU)": "AA",
        " BBB+ ": "BBB+",
        "Рейтинг отозван": None,
    }.items():
        with subtests.test(raw):
            assert make_item(rating_value=raw).rating_value == expected


def test_empty_optional_fields_become_none(make_item):
    item = make_item(inn="", isin="", ko_number="", subject_name="", prediction="")

    assert item.inn is None
    assert item.isin is None
    assert item.ko_number is None
    assert item.subject_name is None
    assert item.prediction is None


def test_accepts_registration_number_instead_of_isin(make_item):
    assert make_item(isin="4B02-06-00124-A-001P").isin == "4B02-06-00124-A-001P"
    assert make_item(isin="-").isin is None


def test_accepts_license_suffix_in_ko_number(make_item):
    assert make_item(ko_number="3306-К").ko_number == "3306-К"


def test_adds_missing_scheme_to_release_url(make_item):
    assert make_item(release_url="example.com/a").release_url == "https://example.com/a"


def test_rejects_values_outside_the_known_formats(make_item, subtests):
    invalid = {
        "country": {"country": "АТЛАНТИДА"},
        "kra": {"kra_code": "АКРА"},
        "action": {"rating_action": "XX - неизвестное действие"},
        "object type": {"object_type": "ZZZZ - неизвестный тип"},
        "prediction": {"prediction": "ZZ - неизвестный"},
        "inn": {"inn": "123"},
        "isin": {"isin": "not-an-isin"},
        "ko number": {"ko_number": "12"},
        "object id": {"object_id": "abc"},
        "empty rating value": {"rating_value": ""},
        "unknown rating value": {"rating_value": "NR"},
    }

    for name, overrides in invalid.items():
        with subtests.test(name), pytest.raises(ValidationError):
            make_item(**overrides)
