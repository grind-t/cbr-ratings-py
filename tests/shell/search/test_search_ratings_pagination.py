from urllib.parse import parse_qs

import httpx
import pytest

from cbr_ratings import CbrRatingsError, search_ratings
from cbr_ratings._shell.search.search_ratings import PAGE_SIZE

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

    assert await search_ratings(client=client) == []


async def test_returns_single_page_results():
    client = _client(_page(["1", "2"], 2))

    items = await search_ratings(client=client)

    assert [item.object_id for item in items] == ["1", "2"]


async def test_collects_every_page_in_order():
    count = PAGE_SIZE + 1
    page1 = [str(i) for i in range(PAGE_SIZE)]
    client = _client(
        _page(["0"], count),
        {1: _page(page1, count), 2: _page(["999"], count)},
    )

    items = await search_ratings(client=client)

    assert [item.object_id for item in items] == [*page1, "999"]


async def test_raises_on_empty_page():
    client = _client(_page(["1"], PAGE_SIZE + 1), {1: _NOT_FOUND})

    with pytest.raises(CbrRatingsError):
        await search_ratings(client=client)
