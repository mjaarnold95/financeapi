from app.services.money import parse_amount_to_minor

def test_parse_minor_integer():
    assert parse_amount_to_minor("-1234", "USD") == -1234

def test_parse_major_decimal():
    assert parse_amount_to_minor("-12.34", "USD") == -1234
    assert parse_amount_to_minor("12.345", "USD") == 1235  # half-up rounding

def test_parse_major_with_commas():
    assert parse_amount_to_minor("1,234.56", "USD") == 123456

def test_parse_jpy_zero_decimals():
    assert parse_amount_to_minor("1000", "JPY") == 1000
    assert parse_amount_to_minor("1000.4", "JPY") == 1000
