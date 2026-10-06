from typing import Literal

Kra = Literal["AKRA", "NKR", "EXPERT_RA", "NRA", "UNKNOWN"]


def convert_kra_name(value: str) -> Kra:
    value = value.upper()

    if "АКРА" in value:
        return "AKRA"
    if "НКР" in value:
        return "NKR"
    if "ЭКСПЕРТ РА" in value:
        return "EXPERT_RA"
    if "НРА" in value:
        return "NRA"
    return "UNKNOWN"
