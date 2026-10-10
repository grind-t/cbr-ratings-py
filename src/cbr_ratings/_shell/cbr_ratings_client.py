import math
from collections.abc import Sequence
from datetime import date
from types import TracebackType
from typing import Self

import httpx

from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.search.bitrix_protocol import parse_csrf_token, serialize_fields
from cbr_ratings._core.search.errors import CbrRatingsError, CsrfTokenRejectedError
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
from cbr_ratings._core.search.search_page import RatingSearchPage

_DISCLAIMER_URL = "https://ratings.cbr.ru/?disclaimer=1"
_AJAX_URL = "https://ratings.cbr.ru/bitrix/services/main/ajax.php"

# The largest page size the site accepts.
_PAGE_SIZE = 100


class CbrRatingsClient:
    """Client of the ratings registry at ratings.cbr.ru.

    The CSRF token is fetched once and reused, so keep one instance for many
    queries. The site keeps the last search in the session cookie, so
    concurrent queries must not share an instance or an `httpx.AsyncClient`.
    Use `async with` to close the internally created `httpx.AsyncClient`.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._own_client = client is None
        self._client = client or httpx.AsyncClient(timeout=30)
        self._csrf_token: str | None = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._own_client:
            await self._client.aclose()

    async def query(
        self,
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
    ) -> list[RatingItem]:
        """Search the ratings registry and return every page of results."""
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
        first = await self._run_action("searchRating", query.to_string())

        if first is None:
            return []

        if first.page_count <= 1:
            return first.item_list

        items: list[RatingItem] = []

        for number in range(1, math.ceil(first.item_count / _PAGE_SIZE) + 1):
            form = serialize_fields(
                {
                    "pageSize": _PAGE_SIZE,
                    "pageNumber": number,
                    "sortingField": "objectName",
                    "sortingDirection": "ascending",
                }
            )
            page = await self._run_action("searchRatingNavigation", form)
            if page is None:
                raise CbrRatingsError(f"Page {number} of the search is empty")
            items.extend(page.item_list)

        return items

    async def _run_action(self, action: str, form: str) -> RatingSearchPage | None:
        """Return None when nothing is found. Refresh a rejected token once."""
        if self._csrf_token is None:
            self._csrf_token = await self._fetch_csrf_token()

        try:
            return await self._post(action, form, self._csrf_token)
        except CsrfTokenRejectedError:
            self._csrf_token = await self._fetch_csrf_token()
            return await self._post(action, form, self._csrf_token)

    async def _fetch_csrf_token(self) -> str:
        response = await self._client.get(_DISCLAIMER_URL)
        response.raise_for_status()
        token = parse_csrf_token(response.text)

        if token is None:
            raise CbrRatingsError("Failed to fetch CSRF token")

        return token

    async def _post(
        self, action: str, form: str, csrf_token: str
    ) -> RatingSearchPage | None:
        response = await self._client.post(
            _AJAX_URL,
            params={"mode": "ajax", "c": "prr.form", "action": action},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "bx-ajax": "true",
                "x-bitrix-csrf-token": csrf_token,
            },
            content=form,
        )
        response.raise_for_status()
        return RatingSearchPage.from_response(response.json())
