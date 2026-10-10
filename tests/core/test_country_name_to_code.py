from typing import get_args

import pytest

from cbr_ratings._core.rating.country import country_name_to_code
from cbr_ratings._core.search.search_form import SearchFormCountry


def test_converts_country_names_to_iso_codes(subtests):
    cases = {
        "РОССИЯ": "RU",
        "ГОНКОНГ": "HK",
        "СОЕДИНЕННОЕ КОРОЛЕВСТВО ВЕЛИКОБРИТАНИИ И СЕВЕРНОЙ ИРЛАНДИИ": "GB",
    }
    for value, expected in cases.items():
        with subtests.test(value=value):
            assert country_name_to_code(value) == expected


def test_international_values_share_one_code(subtests):
    values = [
        "международная компания, зарегистрированная в порядке инкорпорации",
        "Международные организации и институты",
        "международная финансовая организация",
    ]
    for value in values:
        with subtests.test(value=value):
            assert country_name_to_code(value) == "INTL"


def test_converts_every_country_of_the_search_form(subtests):
    for name in get_args(SearchFormCountry):
        with subtests.test(name=name):
            assert country_name_to_code(name)


def test_rejects_unknown_country_names():
    with pytest.raises(ValueError, match="unknown country name"):
        country_name_to_code("АТЛАНТИДА")
