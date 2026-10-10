from typing import Literal

KraCode = Literal["AKRA", "NKR", "EXPERT_RA", "NRA"]

_KRA_BY_NAME: dict[str, KraCode] = {
    "АКРА (АО)": "AKRA",
    'ООО "НКР"': "NKR",
    'АО "Эксперт РА"': "EXPERT_RA",
    'ООО "НРА"': "NRA",
}


def convert_kra_name(value: str) -> KraCode:
    try:
        return _KRA_BY_NAME[value]
    except KeyError:
        raise ValueError(f"unknown KRA name: {value!r}") from None
