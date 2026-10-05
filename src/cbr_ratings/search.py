import math
import re
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any
from urllib.parse import quote

import httpx

from .schema import (
    Country,
    KraName,
    RatingAction,
    RatingGroup,
    RatingItem,
    RatingScale,
    RatingSearchPage,
    RatingStatus,
    TypeGroup,
)

_DISCLAIMER_URL = "https://ratings.cbr.ru/?disclaimer=1"
_AJAX_URL = "https://ratings.cbr.ru/bitrix/services/main/ajax.php"
_CSRF_TOKEN_RE = re.compile(r'"bitrix_sessid":.*?"(.+?)"')
_NOT_FOUND_ERROR = {"message": "Array", "code": 0, "customData": None}
# The largest page size the site accepts.
_PAGE_SIZE = 100

FieldValue = str | int | Sequence[str | int] | None


class CbrRatingsError(Exception):
    pass


def serialize_fields(fields: Mapping[str, FieldValue], prefix: str = "fields") -> str:
    """Encode fields the way Bitrix expects: fields[key]=v, fields[key][0]=v."""
    parts: list[str] = []

    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, str | int):
            parts.append(f"{prefix}[{key}]={_encode(value)}")
        else:
            for i, item in enumerate(value):
                parts.append(f"{prefix}[{key}][{i}]={_encode(item)}")

    return "&".join(parts)


def _encode(value: str | int) -> str:
    # Same safe set as JS encodeURIComponent.
    return quote(str(value), safe="-_.!~*'()")


async def fetch_csrf_token(client: httpx.AsyncClient) -> str | None:
    response = await client.get(_DISCLAIMER_URL)
    response.raise_for_status()
    match = _CSRF_TOKEN_RE.search(response.text)
    return match[1] if match else None


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
    if client is None:
        async with httpx.AsyncClient(timeout=30) as own_client:
            return await search_ratings(
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
                client=own_client,
            )

    csrf_token = await fetch_csrf_token(client)

    if csrf_token is None:
        raise CbrRatingsError("Failed to fetch CSRF token")

    page = await _run_action(
        client,
        csrf_token,
        "searchRating",
        {
            "formSearh": "advanced",
            "dateFrom": _format_date(date_from),
            "dateTo": _format_date(date_to),
            "ratingName": rating_name,
            "inn": inn,
            "isin": isin,
            "koNumber": ko_number,
            "country": country,
            "typeGroup": type_group,
            "kraName": kra_name,
            "ratingScale": rating_scale,
            "ratingGroup": rating_group,
            "ratingAction": rating_action,
            "ratingStatus": rating_status,
        },
    )

    if page is None:
        return []

    if page.page_count <= 1:
        return page.item_list

    items: list[RatingItem] = []

    for page_number in range(1, math.ceil(page.item_count / _PAGE_SIZE) + 1):
        page = await _run_action(
            client,
            csrf_token,
            "searchRatingNavigation",
            {
                "pageSize": _PAGE_SIZE,
                "pageNumber": page_number,
                "sortingField": "objectName",
                "sortingDirection": "ascending",
            },
        )
        if page is None:
            raise CbrRatingsError(f"Page {page_number} of the search is empty")
        items.extend(page.item_list)

    return items


async def _run_action(
    client: httpx.AsyncClient,
    csrf_token: str,
    action: str,
    fields: Mapping[str, FieldValue],
) -> RatingSearchPage | None:
    """Return None when nothing is found."""
    response = await client.post(
        _AJAX_URL,
        params={"mode": "ajax", "c": "prr.form", "action": action},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "bx-ajax": "true",
            "x-bitrix-csrf-token": csrf_token,
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


def _format_date(value: date | None) -> str | None:
    return value.strftime("%d.%m.%Y") if value else None
