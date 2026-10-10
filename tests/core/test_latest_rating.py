from cbr_ratings._core.rating.latest_rating import (
    latest_rating,
    latest_ratings_by_kra,
)


def test_returns_the_newest_non_withdrawn_rating(make_item):
    older = make_item(release_date="01.01.2020", rating_code="BBB")
    newer = make_item(release_date="02.02.2021", rating_code="AA")

    assert latest_rating([newer, older]) is newer
    assert latest_rating([older, newer]) is newer


def test_compares_dates_not_strings(make_item):
    # "31.01.2020" > "01.02.2021" as strings
    older = make_item(release_date="31.01.2020")
    newer = make_item(release_date="01.02.2021")

    assert latest_rating([older, newer]) is newer


def test_ignores_withdrawn_ratings(make_item):
    withdrawn_newest = make_item(
        release_date="10.10.2022", rating_code="Рейтинг отозван"
    )
    older = make_item(release_date="01.01.2021", rating_code="B")

    assert latest_rating([withdrawn_newest, older]) is older


def test_returns_none_when_all_ratings_are_withdrawn(make_item):
    a = make_item(release_date="01.01.2020", rating_code="рейтинг отозван")
    b = make_item(
        release_date="02.02.2021",
        rating_code="BBB",
        rating_action="WD - отзыв кредитного рейтинга",
    )

    assert latest_rating([a, b]) is None


def test_by_kra_returns_empty_dict_for_empty_input():
    assert latest_ratings_by_kra([]) == {}


def test_by_kra_returns_the_newest_item_per_kra(make_item):
    older = make_item(
        kra_code="АКРА (АО)", rating_code="BBB", release_date="01.01.2020"
    )
    newer = make_item(kra_code="АКРА (АО)", rating_code="AA", release_date="05.05.2023")

    assert latest_ratings_by_kra([older, newer]) == {"AKRA": newer}


def test_by_kra_groups_items_by_kra(make_item):
    akra = make_item(kra_code="АКРА (АО)", rating_code="AA")
    nkr = make_item(kra_code='ООО "НКР"', rating_code="BBB")
    expert = make_item(kra_code='АО "Эксперт РА"', rating_code="A")
    nra = make_item(kra_code='ООО "НРА"', rating_code="BB")

    assert latest_ratings_by_kra([akra, nkr, expert, nra]) == {
        "AKRA": akra,
        "NKR": nkr,
        "EXPERT_RA": expert,
        "NRA": nra,
    }


def test_by_kra_omits_kra_where_all_are_withdrawn(make_item):
    withdrawn_akra = make_item(kra_code="АКРА (АО)", rating_code="Рейтинг отозван")
    valid_nkr = make_item(kra_code='ООО "НКР"', rating_code="A")

    assert latest_ratings_by_kra([withdrawn_akra, valid_nkr]) == {"NKR": valid_nkr}
