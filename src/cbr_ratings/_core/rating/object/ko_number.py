from typing import Annotated

from pydantic import BeforeValidator, StringConstraints

from cbr_ratings._core.rating.api_values import empty_to_none

# Only credit organizations have one: "1234", or "3306-ЦК" for a special license.
KoNumber = Annotated[
    Annotated[str, StringConstraints(pattern=r"^\d{4}(?:-[А-Я]{1,2})?$")] | None,
    BeforeValidator(empty_to_none),
]
