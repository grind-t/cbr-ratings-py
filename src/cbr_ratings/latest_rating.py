from collections.abc import Iterable
from datetime import date

from .kra import Kra, convert_kra_name
from .schema import RatingItem
from .withdrawn import is_rating_withdrawn


def latest_rating(items: Iterable[RatingItem]) -> RatingItem | None:
    active = [
        item
        for item in items
        if not is_rating_withdrawn(item.rating_value, item.rating_action)
    ]
    return max(active, key=_release_date) if active else None


def _release_date(item: RatingItem) -> date:
    return item.release_date


def latest_ratings_by_kra(items: Iterable[RatingItem]) -> dict[Kra, RatingItem]:
    groups: dict[Kra, list[RatingItem]] = {}
    for item in items:
        groups.setdefault(convert_kra_name(item.kra_name), []).append(item)

    result: dict[Kra, RatingItem] = {}
    for kra, group in groups.items():
        if (latest := latest_rating(group)) is not None:
            result[kra] = latest
    return result
