import pytest

from cbr_ratings._core.errors import CbrRatingsError
from cbr_ratings._core.query import RatingQuery
from cbr_ratings._core.rating_item import RatingItem
from cbr_ratings._core.rating_search_page import RatingSearchPage
from cbr_ratings._usecases.search import PAGE_SIZE, search_all


def make_page(items: list[RatingItem], item_count: int) -> RatingSearchPage:
    return RatingSearchPage(
        page_count=-(-item_count // 25),
        page_number=1,
        sorting_field="objectName",
        sorting_direction="ascending",
        page_size=25,
        item_list=items,
        item_count=item_count,
    )


class FakeSource:
    """Port fake: the first page plus the pages requested afterwards."""

    def __init__(
        self,
        first: RatingSearchPage | None,
        pages: dict[int, RatingSearchPage | None] | None = None,
    ):
        self.first = first
        self.pages = pages or {}
        self.requested: list[tuple[int, int]] = []

    async def first_page(self, query: RatingQuery) -> RatingSearchPage | None:
        return self.first

    async def page(self, number: int, size: int) -> RatingSearchPage | None:
        self.requested.append((number, size))
        return self.pages[number]


async def test_returns_empty_list_when_nothing_is_found():
    assert await search_all(FakeSource(None), RatingQuery()) == []


async def test_returns_single_page_without_navigation(make_item):
    items = [make_item(isin="A"), make_item(isin="B")]
    source = FakeSource(make_page(items, 2))

    assert await search_all(source, RatingQuery()) == items
    assert source.requested == []


async def test_collects_every_page(make_item):
    first = [make_item(isin="first")]
    page1 = [make_item(isin=str(i)) for i in range(PAGE_SIZE)]
    page2 = [make_item(isin="last")]
    source = FakeSource(
        make_page(first, PAGE_SIZE + 1),
        {1: make_page(page1, PAGE_SIZE + 1), 2: make_page(page2, PAGE_SIZE + 1)},
    )

    assert await search_all(source, RatingQuery()) == page1 + page2
    assert source.requested == [(1, PAGE_SIZE), (2, PAGE_SIZE)]


async def test_raises_on_empty_page(make_item):
    source = FakeSource(make_page([make_item()], PAGE_SIZE + 1), {1: None})

    with pytest.raises(CbrRatingsError, match="Page 1"):
        await search_all(source, RatingQuery())
