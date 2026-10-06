import asyncio
import logging
import os
from datetime import date

from _export import WINDOW_MONTHS, collect_latest_ratings, months_ago, write_export
from moex import get_moex_bond_securities
from t_tech.invest import AsyncClient

from cbr_ratings import RatingItem, search_ratings

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

    date_from = months_ago(date.today(), WINDOW_MONTHS)  # noqa: DTZ011

    async def search(inn: str) -> list[RatingItem]:
        return await search_ratings(
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

    write_export("issuers.json.br", await collect_latest_ratings(sorted(inns), search))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(main())
