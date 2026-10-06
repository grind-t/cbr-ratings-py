import re

# WD as a standalone code, so that WDP (withdrawn prediction) does not match.
_WITHDRAWN_ACTION_RE = re.compile(r"\bWD\b")


def is_rating_withdrawn(value: str, action: str | None = None) -> bool:
    return value.lower() == "рейтинг отозван" or (
        action is not None and _WITHDRAWN_ACTION_RE.search(action) is not None
    )
