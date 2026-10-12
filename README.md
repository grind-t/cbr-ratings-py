# grind-t-cbr-ratings

[![Weekly Export](https://github.com/grind-t/cbr-ratings-py/actions/workflows/weekly-export.yml/badge.svg?branch=main)](https://github.com/grind-t/cbr-ratings-py/actions/workflows/weekly-export.yml)

Async Python client for the [Bank of Russia credit ratings registry](https://ratings.cbr.ru/).
Python port of [`@grind-t/cbr-ratings`](https://github.com/grind-t/cbr-ratings).

## Installation

```sh
uv add grind-t-cbr-ratings
```

## Usage

```python
import asyncio
from datetime import date

import httpx
from cbr_ratings import CbrRatingsClient


async def main():
    async with httpx.AsyncClient(timeout=30) as http:
        client = CbrRatingsClient(http)
        items = await client.query(
            isin="RU000A1025U5",
            date_from=date(2020, 1, 1),
            type_group=["Финансовые инструменты"],
        )

    for item in items:
        print(
            item.kra_code,
            item.rating_code,
            item.prediction,
        )


asyncio.run(main())
```

## API

| Name | Description |
| --- | --- |
| `CbrRatingsClient(...).query(...)` | Search the registry; all filters of the site's advanced form |
| `RatingItem` | Pydantic model of one registry row; the type of items returned by `query`. Also validates its own dump, e.g. the files in `exports/` |
| `KraCode` | Credit rating agency code: `AKRA`, `NKR`, `EXPERT_RA`, `NRA` |
| `Prediction` | Rating outlook code: `STA`, `POS`, `NEG`, `DEV` |
| `latest_rating(items)` | Newest non-withdrawn rating, or `None` |
| `latest_ratings_by_kra(items)` | Newest non-withdrawn rating per agency |

All of them are importable from the package root: `from cbr_ratings import ...`.
