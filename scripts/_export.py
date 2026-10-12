import logging
from datetime import date
from pathlib import Path

import brotli
from dateutil.relativedelta import relativedelta
from pydantic import TypeAdapter

from cbr_ratings import KraCode, RatingItem

EXPORTS_DIR = Path(__file__).parent.parent / "exports"

_EXPORT_SCHEMA = TypeAdapter(dict[str, dict[KraCode, RatingItem]])

logger = logging.getLogger(__name__)


def stale_cutoff_date() -> date:
    return date.today() - relativedelta(months=9)  # noqa: DTZ011


def write_export(name: str, ratings: dict[str, dict[KraCode, RatingItem]]) -> None:
    payload = _EXPORT_SCHEMA.dump_json(dict(sorted(ratings.items())))
    (EXPORTS_DIR / name).write_bytes(brotli.compress(payload))
    logger.info("Wrote %d entries to %s", len(ratings), name)
