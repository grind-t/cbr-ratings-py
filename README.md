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

import cbr_ratings


async def main():
    items = await cbr_ratings.search_ratings(
        isin="RU000A1025U5",
        date_from=date(2020, 1, 1),
        type_group=["Финансовые инструменты"],
    )

    for kra, item in cbr_ratings.latest_ratings_by_kra(items).items():
        print(
            kra,
            item.rating_code,
            item.prediction,
        )


asyncio.run(main())
```

`search_ratings` returns every page of results and an empty list when nothing
is found. It accepts an optional `client: httpx.AsyncClient`; the site keeps the
last search in the session cookie, so concurrent searches must not share one.

## API

| Name | Description |
| --- | --- |
| `search_ratings(...)` | Search the registry; all filters of the site's advanced form |
| `latest_rating(items)` | Newest non-withdrawn rating |
| `latest_ratings_by_kra(items)` | Newest non-withdrawn rating per agency |
| `convert_country(name)` | `"РОССИЯ"` → `"RU"`; international organizations → `"INTL"` |
| `convert_kra_name(name)` | `"АКРА (АО)"` → `"AKRA"` |
| `rating_code_to_number(value)` | `"ruAA-"` → `20`, index in `RATING_SCALE` |
| `convert_prediction(value)` | `"STA - стабильный"` → `"STA"` |
| `is_rating_withdrawn(value, action)` | Withdrawn by value or `WD` action |
| `LatestRating.from_item(item)` | Rating value, prediction and date only |

## Exports

A weekly workflow publishes the latest rating of every agency for bonds traded
on T-Invest, as Brotli-compressed JSON:

- [`exports/bonds.json.br`](exports/bonds.json.br): keyed by ISIN
- [`exports/issuers.json.br`](exports/issuers.json.br): keyed by issuer INN

```json
{"RU000A1025U5": {"AKRA": {"value": 23, "prediction": "STA", "release_date": "2026-03-01"}}}
```

`value` is the index in `RATING_SCALE` (`null` when it is not on the scale), and
agencies are `AKRA`, `NKR`, `EXPERT_RA` and `NRA`.

Run an export locally with `T_INVEST_READONLY_TOKEN` set:

```sh
uv run scripts/export_bonds.py
uv run scripts/export_issuers.py
```
