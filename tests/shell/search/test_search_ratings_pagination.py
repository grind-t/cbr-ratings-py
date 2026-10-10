import httpx
import pytest

from cbr_ratings import CbrRatingsError, search_ratings
from cbr_ratings._shell.search.search_ratings import PAGE_SIZE

_NOT_FOUND = {
    "status": "error",
    "errors": [{"message": "Array", "code": 0, "customData": None}],
}


def _item(isin: str) -> dict:
    return {
        "ratingAction": "",
        "country": "РОССИЯ",
        "koNumber": "",
        "releaseDate": "01.01.2000",
        "inn": "",
        "objectType": "",
        "ratingValue": "BBB",
        "prediction": "",
        "objectName": "",
        "kraName": "",
        "releaseUrl": "",
        "objectId": "",
        "isin": isin,
        "subjectName": "",
    }


def _page(isins: list[str], item_count: int) -> dict:
    return {
        "status": "success",
        "data": {
            "pageCount": -(-item_count // 25),
            "pageNumber": 1,
            "sortingField": "objectName",
            "sortingDirection": "ascending",
            "pageSize": 25,
            "itemList": [_item(isin) for isin in isins],
            "itemCount": item_count,
        },
    }


def _client(
    first: dict, pages: dict[int, dict] | None = None
) -> tuple[httpx.AsyncClient, list[tuple[int, int]]]:
    """A client answering like the site; also returns the requested (number, size)."""
    requested: list[tuple[int, int]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, text='{"bitrix_sessid": "token"}')

        if request.url.params["action"] == "searchRating":
            return httpx.Response(200, json=first)

        body = request.content.decode()
        number = int(body.split("pageNumber]=")[1].split("&")[0])
        size = int(body.split("pageSize]=")[1].split("&")[0])
        requested.append((number, size))
        return httpx.Response(200, json=(pages or {})[number])

    return httpx.AsyncClient(transport=httpx.MockTransport(handler)), requested


async def test_returns_empty_list_when_nothing_is_found():
    client, _ = _client(_NOT_FOUND)

    assert await search_ratings(client=client) == []


async def test_returns_single_page_without_navigation():
    client, requested = _client(_page(["A", "B"], 2))

    items = await search_ratings(client=client)

    assert [item.isin for item in items] == ["A", "B"]
    assert requested == []


async def test_collects_every_page():
    count = PAGE_SIZE + 1
    page1 = [str(i) for i in range(PAGE_SIZE)]
    client, requested = _client(
        _page(["first"], count),
        {1: _page(page1, count), 2: _page(["last"], count)},
    )

    items = await search_ratings(client=client)

    assert [item.isin for item in items] == [*page1, "last"]
    assert requested == [(1, PAGE_SIZE), (2, PAGE_SIZE)]


async def test_raises_on_empty_page():
    client, _ = _client(_page(["A"], PAGE_SIZE + 1), {1: _NOT_FOUND})

    with pytest.raises(CbrRatingsError, match="Page 1"):
        await search_ratings(client=client)
