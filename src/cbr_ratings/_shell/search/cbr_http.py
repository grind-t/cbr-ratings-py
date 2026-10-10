import httpx

from cbr_ratings._core.search.bitrix_protocol import parse_csrf_token, serialize_fields
from cbr_ratings._core.search.errors import CbrRatingsError
from cbr_ratings._core.search.query import RatingQuery
from cbr_ratings._core.search.search_page import RatingSearchPage

_DISCLAIMER_URL = "https://ratings.cbr.ru/?disclaimer=1"
_AJAX_URL = "https://ratings.cbr.ru/bitrix/services/main/ajax.php"


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

        return await self._run_action("searchRating", query.to_string())

    async def page(self, number: int, size: int) -> RatingSearchPage | None:
        form = serialize_fields(
            {
                "pageSize": size,
                "pageNumber": number,
                "sortingField": "objectName",
                "sortingDirection": "ascending",
            }
        )
        return await self._run_action("searchRatingNavigation", form)

    async def _run_action(self, action: str, form: str) -> RatingSearchPage | None:
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
            content=form,
        )
        response.raise_for_status()
        return RatingSearchPage.from_response(response.json())


async def fetch_csrf_token(client: httpx.AsyncClient) -> str | None:
    response = await client.get(_DISCLAIMER_URL)
    response.raise_for_status()
    return parse_csrf_token(response.text)
