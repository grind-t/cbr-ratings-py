import asyncio
import logging
import os

import httpx
from _export import stale_cutoff_date, write_export
from moex import get_moex_bond_securities
from t_tech.invest import AsyncClient

from cbr_ratings import CbrRatingsClient
from cbr_ratings._core.rating.kra import KraCode
from cbr_ratings._core.rating.latest_rating import latest_ratings_by_kra
from cbr_ratings._core.rating.rating_item import RatingItem

logger = logging.getLogger(__name__)


async def main() -> None:
    async with AsyncClient(os.environ["T_INVEST_READONLY_TOKEN"]) as t_invest:
        bonds, moex_securities = await asyncio.gather(
            t_invest.instruments.bonds(), get_moex_bond_securities()
        )

    inn_by_isin = {s.isin: s.emitent_inn for s in moex_securities if s.isin}
    inns: set[str] = set()

    for bond in bonds.instruments:
        if inn := inn_by_isin.get(bond.isin):
            inns.add(inn)
        else:
            logger.warning("Missing issuer inn for bond with isin %s", bond.isin)

    date_from = stale_cutoff_date()

    async with httpx.AsyncClient(timeout=30) as http:
        client = CbrRatingsClient(http)

        ratings: dict[str, dict[KraCode, RatingItem]] = {}

        for inn in sorted(inns):
            items = await client.query(
                inn=inn,
                date_from=date_from,
                type_group=[
                    "Негосударственные пенсионные фонды",
                    "Страховые организации",
                    "Прочие организации",
                    "Лизинговые компании",
                    "Кредитные организации",
                    "Микрофинансовые организации",
                    "Объекты суверенного кредитного рейтинга",
                ],
            )

            if not items:
                logger.info("Missing ratings for %s", inn)
                continue

            if by_kra := latest_ratings_by_kra(items):
                ratings[inn] = by_kra

        write_export("issuers.json.br", ratings)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(main())
