from typing import Literal, get_args

from cbr_ratings._core.rating.api_values import leading_code

Prediction = Literal["STA", "POS", "NEG", "DEV"]

# NA: the methodology has no prediction, OP: other, UNW: undetermined.
_NO_PREDICTION_CODES = ("NA", "OP", "UNW")


def convert_prediction(value: str | None) -> Prediction | None:
    """'STA - стабильный' -> 'STA'; no usable prediction -> None."""
    code = leading_code(value)
    if code is None or code in _NO_PREDICTION_CODES:
        return None
    for prediction in get_args(Prediction):
        if code == prediction:
            return prediction
    raise ValueError(f"unknown prediction: {value!r}")
