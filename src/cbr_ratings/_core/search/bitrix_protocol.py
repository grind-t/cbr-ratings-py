import re
from collections.abc import Mapping, Sequence
from urllib.parse import quote

_CSRF_TOKEN_RE = re.compile(r'"bitrix_sessid":.*?"(.+?)"')

FieldValue = str | int | Sequence[str | int] | None


def parse_csrf_token(html: str) -> str | None:
    match = _CSRF_TOKEN_RE.search(html)
    return match[1] if match else None


def serialize_fields(fields: Mapping[str, FieldValue], prefix: str = "fields") -> str:
    """Encode fields the way Bitrix expects: fields[key]=v, fields[key][0]=v."""
    parts: list[str] = []

    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, str | int):
            parts.append(f"{prefix}[{key}]={_encode(value)}")
        else:
            parts.extend(
                f"{prefix}[{key}][{i}]={_encode(item)}" for i, item in enumerate(value)
            )

    return "&".join(parts)


def _encode(value: str | int) -> str:
    # Same safe set as JS encodeURIComponent.
    return quote(str(value), safe="-_.!~*'()")
