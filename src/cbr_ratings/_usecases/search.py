import math

from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.search.query import RatingQuery
from cbr_ratings._ports.ratings_source import RatingsSource

# The largest page size the site accepts.
PAGE_SIZE = 100


async def search_all(source: RatingsSource, query: RatingQuery) -> list[RatingItem]:
    """Return every page of results, or an empty list when nothing is found."""
    page = await source.first_page(query)

    if page is None:
        return []

    if page.page_count <= 1:
        return page.item_list

    items: list[RatingItem] = []

    for number in range(1, math.ceil(page.item_count / PAGE_SIZE) + 1):
        next_page = await source.page(number, PAGE_SIZE)
        if next_page is None:
            raise CbrRatingsError(f"Page {number} of the search is empty")
        items.extend(next_page.item_list)

    return items
