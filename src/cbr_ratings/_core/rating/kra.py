from typing import Literal

Kra = Literal["AKRA", "NKR", "EXPERT_RA", "NRA"]

_KRA_BY_NAME: dict[str, Kra] = {
    "АКРА (АО)": "AKRA",
    'ООО "НКР"': "NKR",
    'АО "Эксперт РА"': "EXPERT_RA",
    'ООО "НРА"': "NRA",
}


def convert_kra(value: str) -> Kra:
    try:
        return _KRA_BY_NAME[value]
    except KeyError:
        raise ValueError(f"unknown KRA name: {value!r}") from None
