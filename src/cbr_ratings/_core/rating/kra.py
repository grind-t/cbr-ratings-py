from typing import Literal, get_args

KraCode = Literal["AKRA", "NKR", "EXPERT_RA", "NRA"]

_KRA_BY_NAME: dict[str, KraCode] = {
    "АКРА (АО)": "AKRA",
    'ООО "НКР"': "NKR",
    'АО "Эксперт РА"': "EXPERT_RA",
    'ООО "НРА"': "NRA",
    # a code maps to itself, so a dumped RatingItem validates back
    **{code: code for code in get_args(KraCode)},
}


def convert_kra_name(value: str) -> KraCode:
    try:
        return _KRA_BY_NAME[value]
    except KeyError:
        raise ValueError(f"unknown KRA name: {value!r}") from None
