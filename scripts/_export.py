import asyncio
import calendar
import json
import logging
from collections.abc import Awaitable, Callable
from datetime import date
from functools import partial
from pathlib import Path

import brotli
import httpx

from cbr_ratings import (
    Kra,
    LatestRating,
    RatingItem,
    latest_ratings_by_kra,
)

EXPORTS_DIR = Path(__file__).parent.parent / "exports"
# Ratings older than this are considered stale.
WINDOW_MONTHS = 9
# Pause between requests to stay polite with ratings.cbr.ru.
REQUEST_DELAY = 0.25
RETRIES = 3

logger = logging.getLogger(__name__)


def months_ago(today: date, months: int) -> date:
    year, month = divmod(today.year * 12 + today.month - 1 - months, 12)
    month += 1
    day = min(today.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


async def collect_latest_ratings(
    keys: list[str], search: Callable[[str], Awaitable[list[RatingItem]]]
) -> dict[str, dict[Kra, LatestRating]]:
    """Map each key (isin or inn) to the latest rating of every known agency."""
    result: dict[str, dict[Kra, LatestRating]] = {}

    for key in keys:
        await asyncio.sleep(REQUEST_DELAY)
        items = await _with_retries(partial(search, key))

        if not items:
            logger.info("Missing ratings for %s", key)
            continue

        ratings: dict[Kra, LatestRating] = {
            kra: LatestRating.from_item(item)
            for kra, item in latest_ratings_by_kra(items).items()
        }

        if ratings:
            result[key] = ratings

    return result


def write_export(name: str, ratings: dict[str, dict[Kra, LatestRating]]) -> None:
    data = {
        key: {kra: rating.model_dump(mode="json") for kra, rating in by_kra.items()}
        for key, by_kra in sorted(ratings.items())
    }
    payload = json.dumps(data, separators=(",", ":")).encode()
    (EXPORTS_DIR / name).write_bytes(brotli.compress(payload))
    logger.info("Wrote %d entries to %s", len(data), name)


async def _with_retries[T](call: Callable[[], Awaitable[T]]) -> T:
    for attempt in range(1, RETRIES + 1):
        try:
            return await call()
        except httpx.HTTPError:
            if attempt == RETRIES:
                raise
            logger.warning("Request failed, retrying", exc_info=True)
            await asyncio.sleep(attempt * 5)
    raise AssertionError("unreachable")
