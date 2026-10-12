import asyncio
import logging
import os

import httpx
from _export import stale_cutoff_date, write_export
from t_tech.invest import AsyncClient

from cbr_ratings import CbrRatingsClient, KraCode, RatingItem, latest_ratings_by_kra

logger = logging.getLogger(__name__)


async def main() -> None:
    async with AsyncClient(os.environ["T_INVEST_READONLY_TOKEN"]) as t_invest:
        bonds = (await t_invest.instruments.bonds()).instruments

    date_from = stale_cutoff_date()

    async with httpx.AsyncClient(timeout=30) as http:
        client = CbrRatingsClient(http)

        isins = sorted({bond.isin for bond in bonds if bond.isin})
        ratings: dict[str, dict[KraCode, RatingItem]] = {}

        for isin in isins:
            items = await client.query(
                isin=isin, date_from=date_from, type_group=["Финансовые инструменты"]
            )

            if not items:
                logger.info("Missing ratings for %s", isin)
                continue

            if by_kra := latest_ratings_by_kra(items):
                ratings[isin] = by_kra

        write_export("bonds.json.br", ratings)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(main())
