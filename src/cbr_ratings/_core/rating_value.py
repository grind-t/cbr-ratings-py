import re

RATING_SCALE = (
    "D",
    "C",
    "CC-",
    "CC",
    "CC+",
    "CCC-",
    "CCC",
    "CCC+",
    "B-",
    "B",
    "B+",
    "BB-",
    "BB",
    "BB+",
    "BBB-",
    "BBB",
    "BBB+",
    "A-",
    "A",
    "A+",
    "AA-",
    "AA",
    "AA+",
    "AAA",
)

_RATING_RE = re.compile(r"[A-D]{1,3}[+-]?", re.IGNORECASE)


def rating_value_to_number(
    value: str, scale: tuple[str, ...] = RATING_SCALE
) -> int | None:
    match = _RATING_RE.search(value)
    if match is None or match[0] not in scale:
        return None
    return scale.index(match[0])
