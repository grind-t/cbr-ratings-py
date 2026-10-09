import re
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any
from urllib.parse import quote

import httpx

from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.search.query import RatingQuery
from cbr_ratings._core.search.rating_search_page import RatingSearchPage

_DISCLAIMER_URL = "https://ratings.cbr.ru/?disclaimer=1"
_AJAX_URL = "https://ratings.cbr.ru/bitrix/services/main/ajax.php"
_CSRF_TOKEN_RE = re.compile(r'"bitrix_sessid":.*?"(.+?)"')
_NOT_FOUND_ERROR = {"message": "Array", "code": 0, "customData": None}

FieldValue = str | int | Sequence[str | int] | None


class CbrHttpSource:
    """Ratings from ratings.cbr.ru.

    The site keeps the last search in the session cookie, so concurrent
    searches must not share a client.
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._csrf_token: str | None = None

    async def first_page(self, query: RatingQuery) -> RatingSearchPage | None:
        self._csrf_token = await fetch_csrf_token(self._client)

        if self._csrf_token is None:
            raise CbrRatingsError("Failed to fetch CSRF token")

        return await self._run_action(
            "searchRating",
            {
                "formSearh": "advanced",
                "dateFrom": _format_date(query.date_from),
                "dateTo": _format_date(query.date_to),
                "ratingName": query.rating_name,
                "inn": query.inn,
                "isin": query.isin,
                "koNumber": query.ko_number,
                "country": query.country,
                "typeGroup": query.type_group,
                "kraName": query.kra_name,
                "ratingScale": query.rating_scale,
                "ratingGroup": query.rating_group,
                "ratingAction": query.rating_action,
                "ratingStatus": query.rating_status,
            },
        )

    async def page(self, number: int, size: int) -> RatingSearchPage | None:
        return await self._run_action(
            "searchRatingNavigation",
            {
                "pageSize": size,
                "pageNumber": number,
                "sortingField": "objectName",
                "sortingDirection": "ascending",
            },
        )

    async def _run_action(
        self, action: str, fields: Mapping[str, FieldValue]
    ) -> RatingSearchPage | None:
        """Return None when nothing is found."""
        if self._csrf_token is None:
            raise CbrRatingsError("No search in progress")

        response = await self._client.post(
            _AJAX_URL,
            params={"mode": "ajax", "c": "prr.form", "action": action},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "bx-ajax": "true",
                "x-bitrix-csrf-token": self._csrf_token,
            },
            content=serialize_fields(fields),
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()

        # The site reports an empty result as this error.
        if body["status"] == "error" and body["errors"] == [_NOT_FOUND_ERROR]:
            return None

        if body["status"] != "success":
            raise CbrRatingsError(body["errors"])

        return RatingSearchPage.model_validate(body["data"])


async def fetch_csrf_token(client: httpx.AsyncClient) -> str | None:
    response = await client.get(_DISCLAIMER_URL)
    response.raise_for_status()
    match = _CSRF_TOKEN_RE.search(response.text)
    return match[1] if match else None


def serialize_fields(fields: Mapping[str, FieldValue], prefix: str = "fields") -> str:
    """Encode fields the way Bitrix expects: fields[key]=v, fields[key][0]=v."""
    parts: list[str] = []

    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, str | int):
            parts.append(f"{prefix}[{key}]={_encode(value)}")
        else:
            parts.extend(
                f"{prefix}[{key}][{i}]={_encode(item)}" for i, item in enumerate(value)
            )

    return "&".join(parts)


def _encode(value: str | int) -> str:
    # Same safe set as JS encodeURIComponent.
    return quote(str(value), safe="-_.!~*'()")


def _format_date(value: date | None) -> str | None:
    return value.strftime("%d.%m.%Y") if value else None
