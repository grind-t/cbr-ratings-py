import asyncio
import logging
import os
from datetime import date

from _export import WINDOW_MONTHS, collect_latest_ratings, months_ago, write_export
from t_tech.invest import AsyncClient

from cbr_ratings import CbrRatingsClient, RatingItem


async def main() -> None:
    async with AsyncClient(os.environ["T_INVEST_READONLY_TOKEN"]) as t_invest:
        bonds = (await t_invest.instruments.bonds()).instruments

    date_from = months_ago(date.today(), WINDOW_MONTHS)  # noqa: DTZ011

    async with CbrRatingsClient() as client:

        async def search(isin: str) -> list[RatingItem]:
            return await client.query(
                isin=isin, date_from=date_from, type_group=["Финансовые инструменты"]
            )

        isins = sorted({bond.isin for bond in bonds if bond.isin})
        write_export("bonds.json.br", await collect_latest_ratings(isins, search))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(main())
