import asyncio
from urllib.parse import parse_qs

import httpx
import pytest

from cbr_ratings import CbrRatingsClient, CbrRatingsError
from cbr_ratings._shell.cbr_ratings_client import _PAGE_SIZE

_NOT_FOUND = {
    "status": "error",
    "errors": [{"message": "Array", "code": 0, "customData": None}],
}


def _item(object_id: str) -> dict:
    return {
        "ratingAction": "AF - подтверждение кредитного рейтинга",
        "country": "РОССИЯ",
        "koNumber": "",
        "releaseDate": "01.01.2000",
        "inn": "",
        "objectType": "TBND - облигационный займ",
        "ratingValue": "BBB",
        "prediction": "STA - стабильный",
        "objectName": "Эмитент",
        "kraName": "АКРА (АО)",
        "releaseUrl": "https://example.com",
        "objectId": object_id,
        "isin": "",
        "subjectName": "",
    }


def _page(ids: list[str], item_count: int) -> dict:
    return {
        "status": "success",
        "data": {
            "pageCount": -(-item_count // 25),
            "pageNumber": 1,
            "sortingField": "objectName",
            "sortingDirection": "ascending",
            "pageSize": 25,
            "itemList": [_item(i) for i in ids],
            "itemCount": item_count,
        },
    }


def _client(first: dict, pages: dict[int, dict] | None = None) -> httpx.AsyncClient:
    """A client answering like the site: the first search, then pages by number."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text='{"bitrix_sessid": "token"}')

        if request.url.params["action"] == "searchRating":
            return httpx.Response(200, json=first)

        number = int(parse_qs(request.content.decode())["fields[pageNumber]"][0])
        return httpx.Response(200, json=(pages or {})[number])

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_returns_empty_list_when_nothing_is_found():
    client = _client(_NOT_FOUND)

    assert await CbrRatingsClient(client).query() == []


async def test_returns_single_page_results():
    client = _client(_page(["1", "2"], 2))

    items = await CbrRatingsClient(client).query()

    assert [item.object_id for item in items] == ["1", "2"]


async def test_collects_every_page_in_order():
    count = _PAGE_SIZE + 1
    page1 = [str(i) for i in range(_PAGE_SIZE)]
    client = _client(
        _page(["0"], count),
        {1: _page(page1, count), 2: _page(["999"], count)},
    )

    items = await CbrRatingsClient(client).query()

    assert [item.object_id for item in items] == [*page1, "999"]


async def test_raises_on_empty_page():
    client = _client(_page(["1"], _PAGE_SIZE + 1), {1: _NOT_FOUND})

    with pytest.raises(CbrRatingsError):
        await CbrRatingsClient(client).query()


async def test_reuses_csrf_token_across_queries():
    gets = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal gets
        if request.method == "GET":
            gets += 1
            return httpx.Response(200, text='{"bitrix_sessid": "token"}')
        return httpx.Response(200, json=_page(["1"], 1))

    client = CbrRatingsClient(httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    await client.query()
    await client.query()

    assert gets == 1


async def test_refreshes_rejected_csrf_token():
    tokens = iter(["stale", "fresh"])

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text=f'{{"bitrix_sessid": "{next(tokens)}"}}')
        if request.headers["x-bitrix-csrf-token"] == "stale":
            rejected = {
                "status": "error",
                "errors": [{"message": "Invalid csrf token", "code": "invalid_csrf"}],
            }
            return httpx.Response(200, json=rejected)
        return httpx.Response(200, json=_page(["1"], 1))

    client = CbrRatingsClient(httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    items = await client.query()

    assert [item.object_id for item in items] == ["1"]


async def test_concurrent_queries_do_not_interleave():
    count = _PAGE_SIZE + 1
    actions: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text='{"bitrix_sessid": "token"}')
        actions.append(request.url.params["action"])
        await asyncio.sleep(0)
        return httpx.Response(200, json=_page(["1"], count))

    client = CbrRatingsClient(httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    await asyncio.gather(client.query(), client.query())

    search, page = "searchRating", "searchRatingNavigation"
    assert actions == [search, page, page, search, page, page]
