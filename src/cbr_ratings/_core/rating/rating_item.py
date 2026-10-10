import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BeforeValidator, StringConstraints

from cbr_ratings._core.search.search_form import Country, KraName
from cbr_ratings._core.shared.cbr_api_model import CbrApiModel

RatingActionCode = Literal[
    "AF", "AFP", "DG", "EWR", "NW", "NWR", "OR", "ORP", "OT", "RWR", "UP", "WD",
    "WDP", "WR",
]  # fmt: skip

ObjectTypeCode = Literal[
    "BNFC", "BNFH", "CBNK", "CO", "FDEP", "FFCT", "FINS", "FLSG", "FMFO", "FNPF",
    "FOFO", "IFO", "SCO", "SF", "SMF", "SO", "TBND", "TMGB", "TMNB", "TO", "TSCB",
    "TSFP",
]  # fmt: skip

# NA: the methodology has no prediction, OP: other, UNW: undetermined.
PredictionCode = Literal["NA", "STA", "POS", "NEG", "DEV", "OP", "UNW"]

# Securities are identified by an ISIN or, for older issues, by a state
# registration number in one of the formats below.
_ISIN = r"[A-Z]{2}[A-Z0-9]{9}\d"
_REGISTRATION_NUMBER = (
    r"\d[A-Z]\d{2}-\d{2}-\d{5}-[A-Z]-\d{3}[A-Z]"
    r"|\d-\d{5}-[A-Z]-\d{3}[A-Z]-\d{2}[A-Z]"
    r"|\d{8}[A-Z]\d{3}[A-Z]"
)
_SECURITY_ID = f"{_ISIN}|{_REGISTRATION_NUMBER}"

_NO_VALUE = ("", "-")


def _parse_release_date(value: object) -> object:
    if isinstance(value, str):
        return datetime.strptime(value, "%d.%m.%Y").date()  # noqa: DTZ007 date only
    return value


def _empty_to_none(value: object) -> object:
    return None if isinstance(value, str) and value.strip() in _NO_VALUE else value


def _leading_code(value: object) -> object:
    """'TBND - bond' -> 'TBND': the code before the dash in "CODE - text"."""
    if isinstance(value, str):
        return value.split(maxsplit=1)[0] if value.strip() else None
    return value


def _parse_rating_actions(value: object) -> object:
    """'AF - ..., AFP - ...' -> ('AF', 'AFP')."""
    if isinstance(value, str):
        return tuple(_leading_code(part) for part in value.split(", ")) if value else ()
    return value


def _add_url_scheme(value: object) -> object:
    if isinstance(value, str) and not re.match(r"https?://", value):
        return f"https://{value}"
    return value


_Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


# Absent for sovereign objects and some foreign issuers.
_Inn = Annotated[
    Annotated[str, StringConstraints(pattern=r"^\d{10}$")] | None,
    BeforeValidator(_empty_to_none),
]
_SecurityId = Annotated[
    Annotated[str, StringConstraints(pattern=f"^(?:{_SECURITY_ID})$")] | None,
    BeforeValidator(_empty_to_none),
]
# Only credit organizations have one: "1234", or "1234-K" for a special license.
_KoNumber = Annotated[
    Annotated[str, StringConstraints(pattern=r"^\d{4}(?:-[А-Я]{1,2})?$")] | None,
    BeforeValidator(_empty_to_none),
]


class RatingItem(CbrApiModel):
    # The API sends "CODE - text" for the code fields; only the code is kept.
    rating_action: Annotated[
        tuple[RatingActionCode, ...], BeforeValidator(_parse_rating_actions)
    ]
    country: Country
    ko_number: _KoNumber
    # "DD.MM.YYYY" in the API.
    release_date: Annotated[date, BeforeValidator(_parse_release_date)]
    inn: _Inn
    object_type: Annotated[ObjectTypeCode, BeforeValidator(_leading_code)]
    # Agency notation, e.g. "ruAA-", "AA(RU)", or "Рейтинг отозван".
    rating_value: _Text
    prediction: Annotated[PredictionCode | None, BeforeValidator(_leading_code)]
    object_name: _Text
    kra_name: KraName
    release_url: Annotated[
        str,
        BeforeValidator(_add_url_scheme),
        StringConstraints(pattern=r"^https?://\S+$"),
    ]
    object_id: Annotated[str, StringConstraints(pattern=r"^\d+$")]
    isin: _SecurityId
    # Only bonds have an issuer name.
    subject_name: Annotated[str | None, BeforeValidator(_empty_to_none)]
