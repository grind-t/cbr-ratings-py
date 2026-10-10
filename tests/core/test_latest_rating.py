from datetime import date

from cbr_ratings._core.rating.latest_rating import (
    LatestRating,
    latest_rating,
    latest_ratings_by_kra,
)
from cbr_ratings._core.rating.rating_item import RatingItem


def test_returns_the_newest_non_withdrawn_rating(make_item):
    older = make_item(release_date="01.01.2020", rating_value="BBB")
    newer = make_item(release_date="02.02.2021", rating_value="AA")

    assert latest_rating([newer, older]) is newer
    assert latest_rating([older, newer]) is newer


def test_compares_dates_not_strings(make_item):
    # "31.01.2020" > "01.02.2021" as strings
    older = make_item(release_date="31.01.2020")
    newer = make_item(release_date="01.02.2021")

    assert latest_rating([older, newer]) is newer


def test_ignores_withdrawn_ratings(make_item):
    withdrawn_newest = make_item(
        release_date="10.10.2022", rating_value="Рейтинг отозван"
    )
    older = make_item(release_date="01.01.2021", rating_value="B")

    assert latest_rating([withdrawn_newest, older]) is older


def test_returns_none_when_all_ratings_are_withdrawn(make_item):
    a = make_item(release_date="01.01.2020", rating_value="рейтинг отозван")
    b = make_item(
        release_date="02.02.2021",
        rating_value="BBB",
        rating_action="WD - отзыв кредитного рейтинга",
    )

    assert latest_rating([a, b]) is None


def test_by_kra_returns_empty_dict_for_empty_input():
    assert latest_ratings_by_kra([]) == {}


def test_by_kra_returns_the_newest_item_per_kra(make_item):
    older = make_item(
        kra_name="АКРА (АО)", rating_value="BBB", release_date="01.01.2020"
    )
    newer = make_item(
        kra_name="АКРА (АО)", rating_value="AA", release_date="05.05.2023"
    )

    assert latest_ratings_by_kra([older, newer]) == {"AKRA": newer}


def test_by_kra_groups_items_by_kra(make_item):
    akra = make_item(kra_name="АКРА (АО)", rating_value="AA")
    nkr = make_item(kra_name='ООО "НКР"', rating_value="BBB")
    expert = make_item(kra_name='АО "Эксперт РА"', rating_value="A")
    nra = make_item(kra_name='ООО "НРА"', rating_value="BB")

    assert latest_ratings_by_kra([akra, nkr, expert, nra]) == {
        "AKRA": akra,
        "NKR": nkr,
        "EXPERT_RA": expert,
        "NRA": nra,
    }


def test_by_kra_omits_kra_where_all_are_withdrawn(make_item):
    withdrawn_akra = make_item(kra_name="АКРА (АО)", rating_value="Рейтинг отозван")
    valid_nkr = make_item(kra_name='ООО "НКР"', rating_value="A")

    assert latest_ratings_by_kra([withdrawn_akra, valid_nkr]) == {"NKR": valid_nkr}


def test_rating_item_accepts_api_camel_case():
    item = RatingItem.model_validate(
        {
            "ratingAction": "AF - подтверждение кредитного рейтинга",
            "country": "РОССИЯ",
            "koNumber": "",
            "releaseDate": "31.10.2023",
            "inn": "7707083893",
            "objectType": "TBND - облигационный займ",
            "ratingValue": "AAA(RU)",
            "prediction": "STA - стабильный",
            "objectName": "Эмитент",
            "kraName": "АКРА (АО)",
            "releaseUrl": "https://example.com",
            "objectId": "1",
            "isin": "",
            "subjectName": "",
        }
    )

    assert item.release_date == date(2023, 10, 31)
    assert item.kra_name == "АКРА (АО)"


def test_latest_rating_from_item(make_item):
    item = make_item(
        rating_value="ruA-", prediction="POS - позитивный", release_date="05.05.2023"
    )

    assert LatestRating.from_item(item) == LatestRating(
        value=17, prediction="POS", release_date=date(2023, 5, 5)
    )
