import asyncio
import logging
import os
from datetime import date

import httpx
from _export import WINDOW_MONTHS, write_export
from dateutil.relativedelta import relativedelta
from t_tech.invest import AsyncClient

from cbr_ratings import CbrRatingsClient
from cbr_ratings._core.rating.kra import KraCode
from cbr_ratings._core.rating.latest_rating import latest_ratings_by_kra
from cbr_ratings._core.rating.rating_item import RatingItem

logger = logging.getLogger(__name__)


async def main() -> None:
    async with AsyncClient(os.environ["T_INVEST_READONLY_TOKEN"]) as t_invest:
        bonds = (await t_invest.instruments.bonds()).instruments

    date_from = date.today() - relativedelta(months=WINDOW_MONTHS)  # noqa: DTZ011

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
