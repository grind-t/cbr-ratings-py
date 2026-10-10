import math
from collections.abc import Sequence
from datetime import date

import httpx

from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.search.query import (
    CountryFilter,
    KraNameFilter,
    RatingActionFilter,
    RatingGroupFilter,
    RatingQuery,
    RatingScaleFilter,
    RatingStatusFilter,
    TypeGroupFilter,
)
from cbr_ratings._shell.search.cbr_http import CbrHttpSource

# The largest page size the site accepts.
PAGE_SIZE = 100


async def search_ratings(
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    rating_name: str | None = None,
    inn: str | None = None,
    isin: str | None = None,
    ko_number: str | None = None,
    country: Sequence[CountryFilter] | None = None,
    type_group: Sequence[TypeGroupFilter] | None = None,
    kra_name: Sequence[KraNameFilter] | None = None,
    rating_scale: Sequence[RatingScaleFilter] | None = None,
    rating_group: Sequence[RatingGroupFilter] | None = None,
    rating_action: Sequence[RatingActionFilter] | None = None,
    rating_status: Sequence[RatingStatusFilter] | None = None,
    client: httpx.AsyncClient | None = None,
) -> list[RatingItem]:
    """Search the ratings registry and return every page of results.

    The site keeps the last search in the session cookie, so concurrent calls
    must not share a client.
    """
    query = RatingQuery(
        date_from=date_from,
        date_to=date_to,
        rating_name=rating_name,
        inn=inn,
        isin=isin,
        ko_number=ko_number,
        country=country,
        type_group=type_group,
        kra_name=kra_name,
        rating_scale=rating_scale,
        rating_group=rating_group,
        rating_action=rating_action,
        rating_status=rating_status,
    )

    if client is None:
        async with httpx.AsyncClient(timeout=30) as own_client:
            return await _search_all(CbrHttpSource(own_client), query)

    return await _search_all(CbrHttpSource(client), query)


async def _search_all(source: CbrHttpSource, query: RatingQuery) -> list[RatingItem]:
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
