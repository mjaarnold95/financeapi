from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# currency minor exponent map (extend later)
MINOR_EXPONENT = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,
}

def parse_amount_to_minor(amount_str: str, currency: str) -> int:
    """
    Parse amount from CSV. Accepts:
    - integer minor units: "-1234"
    - decimal major units: "-12.34"
    Returns integer minor units.
    """
    currency = (currency or "USD").upper()
    exp = MINOR_EXPONENT.get(currency, 2)

    s = (amount_str or "").strip()
    if s == "":
        raise ValueError("amount is empty")

    # If it's an integer with no decimal point, treat as minor units.
    if "." not in s and "," not in s:
        # allow leading +/-
        try:
            return int(s)
        except ValueError as e:
            raise ValueError(f"invalid integer amount: {amount_str}") from e

    # Otherwise treat as major units (strip commas)
    s2 = s.replace(",", "")
    try:
        d = Decimal(s2)
    except InvalidOperation as e:
        raise ValueError(f"invalid decimal amount: {amount_str}") from e

    scale = Decimal(10) ** exp
    minor = (d * scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(minor)
