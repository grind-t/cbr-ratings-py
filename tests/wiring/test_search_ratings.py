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


async def test_returns_empty_list_when_nothing_is_found():
    assert await search_ratings(isin="XX000A000000") == []


async def test_returns_every_page():
    # Sberbank has well over one page of ratings
    items = await search_ratings(inn="7707083893", date_from=date(2015, 1, 1))

    assert len(items) > 25
    assert len({item.object_id + item.release_url for item in items}) > 25
