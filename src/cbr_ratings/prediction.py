import re
from typing import Literal, get_args

Prediction = Literal["STA", "POS", "NEG", "DEV"]

_PREDICTION_RE = re.compile(r"^([A-Z]+)")


def convert_prediction(value: str | None) -> Prediction | None:
    match = _PREDICTION_RE.match(value or "")
    code = match[1] if match else ""
    return next((p for p in get_args(Prediction) if p == code), None)
