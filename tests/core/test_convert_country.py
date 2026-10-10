from typing import get_args

import pytest

from cbr_ratings._core.rating.country import Country, convert_country
from cbr_ratings._core.search.query import CountryFilter


def test_converts_country_names_to_iso_codes(subtests):
    cases = {
        "РОССИЯ": "RU",
        "ГОНКОНГ": "HK",
        "СОЕДИНЕННОЕ КОРОЛЕВСТВО ВЕЛИКОБРИТАНИИ И СЕВЕРНОЙ ИРЛАНДИИ": "GB",
    }
    for value, expected in cases.items():
        with subtests.test(value=value):
            assert convert_country(value) == expected


def test_international_values_share_one_code(subtests):
    values = [
        "международная компания, зарегистрированная в порядке инкорпорации",
        "Международные организации и институты",
        "международная финансовая организация",
    ]
    for value in values:
        with subtests.test(value=value):
            assert convert_country(value) == "INTL"


def test_converts_every_country_of_the_search_form(subtests):
    for name in get_args(CountryFilter):
        with subtests.test(name=name):
            assert convert_country(name) in get_args(Country)


def test_rejects_unknown_country_names():
    with pytest.raises(ValueError, match="unknown country name"):
        convert_country("АТЛАНТИДА")
