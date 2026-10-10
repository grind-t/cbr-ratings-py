# Securities are identified by an ISIN or, for older issues, by a state
# registration number in one of the formats below.
_ISIN = r"[A-Z]{2}[A-Z0-9]{9}\d"
_REGISTRATION_NUMBER = (
    r"\d[A-Z]\d{2}-\d{2}-\d{5}-[A-Z]-\d{3}[A-Z]"
    r"|\d-\d{5}-[A-Z]-\d{3}[A-Z]-\d{2}[A-Z]"
    r"|\d{8}[A-Z]\d{3}[A-Z]"
)

SECURITY_ID_PATTERN = f"^(?:{_ISIN}|{_REGISTRATION_NUMBER})$"
