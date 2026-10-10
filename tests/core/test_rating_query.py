from datetime import date

from cbr_ratings._core.search.query import RatingQuery


def test_fields_use_site_names():
    query = RatingQuery(isin="RU000A0JX0J2", kra_name=["АКРА (АО)"])

    fields = query.to_fields()

    assert fields["isin"] == "RU000A0JX0J2"
    assert fields["kraName"] == ["АКРА (АО)"]
    assert fields["formSearh"] == "advanced"


def test_fields_format_dates():
    query = RatingQuery(date_from=date(2024, 3, 5))

    fields = query.to_fields()

    assert fields["dateFrom"] == "05.03.2024"
    assert fields["dateTo"] is None


def test_to_string_skips_unset_fields():
    query = RatingQuery(isin="RU000A0JX0J2")

    assert query.to_string() == "fields[formSearh]=advanced&fields[isin]=RU000A0JX0J2"
