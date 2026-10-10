from datetime import date
from urllib.parse import unquote

from cbr_ratings._core.search.query import RatingQuery


def test_to_string_uses_site_field_names():
    query = RatingQuery(isin="RU000A0JX0J2", kra_name=["АКРА (АО)"])

    body = unquote(query.to_string())

    assert "fields[formSearh]=advanced" in body
    assert "fields[isin]=RU000A0JX0J2" in body
    assert "fields[kraName][0]=АКРА (АО)" in body


def test_to_string_formats_dates():
    query = RatingQuery(date_from=date(2024, 3, 5))

    assert "fields[dateFrom]=05.03.2024" in query.to_string()


def test_to_string_skips_unset_fields():
    query = RatingQuery(isin="RU000A0JX0J2")

    assert query.to_string() == "fields[formSearh]=advanced&fields[isin]=RU000A0JX0J2"
