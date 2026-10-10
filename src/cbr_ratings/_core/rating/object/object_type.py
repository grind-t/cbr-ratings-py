from typing import Annotated, Literal

from pydantic import BeforeValidator

from cbr_ratings._core.rating.api_values import leading_code

ObjectTypeCode = Literal[
    "BNFC", "BNFH", "CBNK", "CO", "FDEP", "FFCT", "FINS", "FLSG", "FMFO", "FNPF",
    "FOFO", "IFO", "SCO", "SF", "SMF", "SO", "TBND", "TMGB", "TMNB", "TO", "TSCB",
    "TSFP",
]  # fmt: skip

# The API sends "CBNK - кредитная организация".
ObjectType = Annotated[ObjectTypeCode, BeforeValidator(leading_code)]
