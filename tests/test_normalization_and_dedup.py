import uuid
from datetime import date

from app.services.normalization import normalize_text, normalize_merchant_name
from app.services.dedup import compute_dedup_hash

def test_normalize_text_basic():
    assert normalize_text("  Hello   world\n") == "HELLO WORLD"
    assert normalize_text("") == ""

def test_normalize_merchant_more_aggressive():
    assert normalize_merchant_name("McDonald's #123") == "MCDONALDS 123"

def test_dedup_hash_stable():
    aid = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    h1 = compute_dedup_hash(
        account_id=aid,
        posted_date=date(2026, 1, 1),
        amount_minor=-1234,
        currency="USD",
        description="Starbucks   001",
    )
    h2 = compute_dedup_hash(
        account_id=aid,
        posted_date=date(2026, 1, 1),
        amount_minor=-1234,
        currency="usd",
        description="  starbucks 001  ",
    )
    assert h1 == h2
