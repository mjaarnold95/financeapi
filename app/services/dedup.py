import hashlib
import uuid
from datetime import date

from app.services.normalization import normalize_text

def compute_dedup_hash(
    *,
    account_id: uuid.UUID,
    posted_date: date,
    amount_minor: int,
    currency: str,
    description: str,
) -> str:
    nd = normalize_text(description)
    key = f"{account_id}|{posted_date.isoformat()}|{amount_minor}|{currency.upper()}|{nd}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
