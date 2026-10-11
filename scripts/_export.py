import json
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

import brotli

from cbr_ratings._core.rating.kra import KraCode
from cbr_ratings._core.rating.latest_rating import latest_ratings_by_kra
from cbr_ratings._core.rating.rating_item import RatingItem

EXPORTS_DIR = Path(__file__).parent.parent / "exports"
# Ratings older than this are considered stale.
WINDOW_MONTHS = 9

logger = logging.getLogger(__name__)


async def collect_latest_ratings(
    keys: list[str], search: Callable[[str], Awaitable[list[RatingItem]]]
) -> dict[str, dict[KraCode, RatingItem]]:
    """Map each key (isin or inn) to the latest rating of every known agency."""
    result: dict[str, dict[KraCode, RatingItem]] = {}

    for key in keys:
        items = await search(key)

        if not items:
            logger.info("Missing ratings for %s", key)
            continue

        if ratings := latest_ratings_by_kra(items):
            result[key] = ratings

    return result


def write_export(name: str, ratings: dict[str, dict[KraCode, RatingItem]]) -> None:
    data = {
        key: {kra: rating.model_dump(mode="json") for kra, rating in by_kra.items()}
        for key, by_kra in sorted(ratings.items())
    }
    payload = json.dumps(data, separators=(",", ":")).encode()
    (EXPORTS_DIR / name).write_bytes(brotli.compress(payload))
    logger.info("Wrote %d entries to %s", len(data), name)
