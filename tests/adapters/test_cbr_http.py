import httpx
import pytest

from cbr_ratings._adapters.cbr_http import CbrHttpSource, fetch_csrf_token
from cbr_ratings._core.query import RatingQuery

pytestmark = pytest.mark.e2e


async def test_fetches_csrf_token():
    async with httpx.AsyncClient() as client:
        token = await fetch_csrf_token(client)

    assert token is not None
    assert len(token) == 32


async def test_first_page_returns_none_when_nothing_is_found():
    async with httpx.AsyncClient(timeout=30) as client:
        page = await CbrHttpSource(client).first_page(RatingQuery(isin="XX000A000000"))

    assert page is None
