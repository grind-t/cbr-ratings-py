from typing import Annotated

from pydantic import BeforeValidator, StringConstraints

from cbr_ratings._core.rating.api_values import empty_to_none

# Absent for sovereign objects and some foreign issuers.
Inn = Annotated[
    Annotated[str, StringConstraints(pattern=r"^\d{10}$")] | None,
    BeforeValidator(empty_to_none),
]
