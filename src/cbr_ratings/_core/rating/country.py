from typing import Literal

# ISO 3166-1 alpha-2 codes, plus INTL (not ISO) for international organizations
# and companies, which have no country.
Country = Literal[
    "AE", "BG", "BY", "CH", "CN", "CY", "CZ", "DE", "GB", "HK", "HU", "IE", "IN",
    "INTL", "JE", "JP", "KG", "KZ", "LU", "LV", "NL", "PL", "RO", "RU", "SG", "SK",
    "TJ", "UZ", "VG",
]  # fmt: skip

_COUNTRY_BY_NAME: dict[str, Country] = {
    "ГОНКОНГ": "HK",
    "СЛОВАКИЯ": "SK",
    "КИРГИЗИЯ": "KG",
    "СИНГАПУР": "SG",
    "ГЕРМАНИЯ": "DE",
    "КАЗАХСТАН": "KZ",
    "КИПР": "CY",
    "ВИРГИНСКИЕ ОСТРОВА, БРИТАНСКИЕ": "VG",
    "ОБЪЕДИНЕННЫЕ АРАБСКИЕ ЭМИРАТЫ": "AE",
    "ПОЛЬША": "PL",
    "НИДЕРЛАНДЫ": "NL",
    "ЯПОНИЯ": "JP",
    "ЛЮКСЕМБУРГ": "LU",
    "ЛАТВИЯ": "LV",
    "КИТАЙ": "CN",
    "РУМЫНИЯ": "RO",
    "ИНДИЯ": "IN",
    "ДЖЕРСИ": "JE",
    "ЧЕШСКАЯ РЕСПУБЛИКА": "CZ",
    "СОЕДИНЕННОЕ КОРОЛЕВСТВО ВЕЛИКОБРИТАНИИ И СЕВЕРНОЙ ИРЛАНДИИ": "GB",
    "УЗБЕКИСТАН": "UZ",
    "ШВЕЙЦАРИЯ": "CH",
    "БЕЛАРУСЬ": "BY",
    "РОССИЯ": "RU",
    "БОЛГАРИЯ": "BG",
    "ВЕНГРИЯ": "HU",
    "ИРЛАНДИЯ": "IE",
    "ТАДЖИКИСТАН": "TJ",
    "международная компания, зарегистрированная в порядке инкорпорации": "INTL",
    "Международные организации и институты": "INTL",
    "Международные компании САР (остров Русский, остров Октябрьский)": "INTL",
    "международная финансовая организация": "INTL",
}


def convert_country(value: str) -> Country:
    try:
        return _COUNTRY_BY_NAME[value]
    except KeyError:
        raise ValueError(f"unknown country name: {value!r}") from None
