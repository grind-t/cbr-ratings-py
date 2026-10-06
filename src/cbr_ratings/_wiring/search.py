from collections.abc import Sequence
from datetime import date

import httpx

from cbr_ratings._adapters.cbr_http import CbrHttpSource
from cbr_ratings._core.query import RatingQuery
from cbr_ratings._core.rating_item import RatingItem
from cbr_ratings._core.search_form import (
    Country,
    KraName,
    RatingAction,
    RatingGroup,
    RatingScale,
    RatingStatus,
    TypeGroup,
)
from cbr_ratings._usecases.search import search_all


async def search_ratings(
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    rating_name: str | None = None,
    inn: str | None = None,
    isin: str | None = None,
    ko_number: str | None = None,
    country: Sequence[Country] | None = None,
    type_group: Sequence[TypeGroup] | None = None,
    kra_name: Sequence[KraName] | None = None,
    rating_scale: Sequence[RatingScale] | None = None,
    rating_group: Sequence[RatingGroup] | None = None,
    rating_action: Sequence[RatingAction] | None = None,
    rating_status: Sequence[RatingStatus] | None = None,
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
            return await search_all(CbrHttpSource(own_client), query)

    return await search_all(CbrHttpSource(client), query)
