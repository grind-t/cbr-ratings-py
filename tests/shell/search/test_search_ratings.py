from collections import Counter
from datetime import date

import pytest

from cbr_ratings import search_ratings

pytestmark = pytest.mark.e2e


async def test_searches_bond_ratings():
    items = await search_ratings(
        isin="RU000A1025U5", type_group=["Финансовые инструменты"]
    )

    assert items
    assert all(item.isin == "RU000A1025U5" for item in items)


async def test_returns_every_page():
    # A whole month is too big for one page, its halves are not.
    whole = await search_ratings(date_from=date(2024, 1, 1), date_to=date(2024, 1, 31))
    first_half = await search_ratings(
        date_from=date(2024, 1, 1), date_to=date(2024, 1, 15)
    )
    second_half = await search_ratings(
        date_from=date(2024, 1, 16), date_to=date(2024, 1, 31)
    )

    assert Counter(map(repr, whole)) == Counter(map(repr, [*first_half, *second_half]))
