from typing import Protocol

from cbr_ratings._core.query import RatingQuery
from cbr_ratings._core.rating_search_page import RatingSearchPage


class RatingsSource(Protocol):
    """A search session: ``page`` continues the last ``first_page`` search.

    Both return None when nothing is found.
    """

    async def first_page(self, query: RatingQuery) -> RatingSearchPage | None: ...

    async def page(self, number: int, size: int) -> RatingSearchPage | None: ...
