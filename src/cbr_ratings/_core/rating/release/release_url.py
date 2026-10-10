import re
from typing import Annotated

from pydantic import BeforeValidator, StringConstraints


def _add_url_scheme(value: object) -> object:
    if isinstance(value, str) and not re.match(r"https?://", value):
        return f"https://{value}"
    return value


ReleaseUrl = Annotated[
    str,
    BeforeValidator(_add_url_scheme),
    StringConstraints(pattern=r"^https?://\S+$"),
]
