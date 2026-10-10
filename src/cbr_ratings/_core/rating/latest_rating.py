from collections.abc import Iterable
from operator import attrgetter

from cbr_ratings._core.rating.kra import KraCode
from cbr_ratings._core.rating.rating_item import RatingItem


def latest_rating(items: Iterable[RatingItem]) -> RatingItem | None:
    active = [
        item
        for item in items
        if item.rating_code is not None and "WD" not in item.rating_action
    ]
    return max(active, key=attrgetter("release_date")) if active else None


def latest_ratings_by_kra(items: Iterable[RatingItem]) -> dict[KraCode, RatingItem]:
    groups: dict[KraCode, list[RatingItem]] = {}
    for item in items:
        groups.setdefault(item.kra_code, []).append(item)

    result: dict[KraCode, RatingItem] = {}
    for kra, group in groups.items():
        if (latest := latest_rating(group)) is not None:
            result[kra] = latest
    return result
