from collections.abc import Collection


def is_rating_withdrawn(value: str, actions: Collection[str] = ()) -> bool:
    """`actions` are rating action codes; WDP (withdrawn prediction) is not WD."""
    return value.lower() == "рейтинг отозван" or "WD" in actions
