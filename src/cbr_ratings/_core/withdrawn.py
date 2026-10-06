def is_rating_withdrawn(value: str, action: str | None = None) -> bool:
    return value.lower() == "рейтинг отозван" or (action is not None and "WD" in action)
