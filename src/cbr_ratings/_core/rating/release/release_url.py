import re


def convert_release_url(value: object) -> object:
    """Add the missing scheme: 'example.com/a' -> 'https://example.com/a'."""
    if isinstance(value, str) and not re.match(r"https?://", value):
        return f"https://{value}"
    return value
