import re
from typing import Annotated, Literal, get_args

from pydantic import BeforeValidator

from cbr_ratings._core.rating.api_values import leading_code

Prediction = Literal["STA", "POS", "NEG", "DEV"]

_PREDICTION_RE = re.compile(r"^([A-Z]+)")


def convert_prediction(value: str | None) -> Prediction | None:
    match = _PREDICTION_RE.match(value or "")
    code = match[1] if match else ""
    return next((p for p in get_args(Prediction) if p == code), None)


# NA: the methodology has no prediction, OP: other, UNW: undetermined.
PredictionCode = Literal["NA", "STA", "POS", "NEG", "DEV", "OP", "UNW"]

# The API sends "STA - стабильный", or "" when there is no prediction.
ItemPrediction = Annotated[PredictionCode | None, BeforeValidator(leading_code)]
