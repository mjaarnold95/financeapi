import csv
import io
import uuid
from datetime import date
from typing import Any

from dateutil.parser import parse as dtparse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Account, CategoryRule, ImportJob, Merchant, Transaction
from app.services.audit import log_audit
from app.services.dedup import compute_dedup_hash
from app.services.money import parse_amount_to_minor
from app.services.normalization import normalize_text, normalize_merchant_name
from app.services.rules_engine import match_category_rule

_ALIASES = {
    "posted_date": {"posted_date", "date", "posted"},
    "authorized_date": {"authorized_date", "auth_date", "authorized"},
    "amount": {"amount", "amt", "amount_minor", "cents"},
    "description": {"description", "memo", "name"},
    "currency": {"currency", "ccy"},
    "provider_txn_id": {"provider_txn_id", "fitid", "transaction_id", "txn_id"},
    "merchant": {"merchant", "payee", "merchant_name"},
}

def _map_headers(headers: list[str]) -> dict[str, str]:
    hmap = {h.strip().lower(): h for h in headers}
    out: dict[str, str] = {}
    for canon, opts in _ALIASES.items():
        for o in opts:
            if o in hmap:
                out[canon] = hmap[o]
                break
    return out

def _parse_date(value: str) -> date:
    d = dtparse(value).date()
    return d

def import_csv_bytes(
    db: Session,
    *,
    account_id: uuid.UUID,
    filename: str | None,
    content: bytes,
) -> tuple[ImportJob, dict[str, int]]:
    account = db.get(Account, account_id)
    if not account:
        raise ValueError(f"account {account_id} not found")

    job = ImportJob(source="csv", filename=filename, status="processing")
    db.add(job)
    db.flush()  # get job.id

    # Preload rules
    rules = db.execute(select(CategoryRule).where(CategoryRule.is_active.is_(True))).scalars().all()

    # Parse CSV
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV missing headers")

    headers_map = _map_headers(reader.fieldnames)

    required = ["posted_date", "amount", "description"]
    for r in required:
        if r not in headers_map:
            raise ValueError(f"CSV missing required column for {r}; headers={reader.fieldnames}")

    stats = {"total_rows": 0, "created": 0, "skipped_duplicates": 0, "categorized": 0}

    for row in reader:
        stats["total_rows"] += 1

        posted_date = _parse_date(row[headers_map["posted_date"]])
        authorized_date = None
        if "authorized_date" in headers_map and row.get(headers_map["authorized_date"]):
            authorized_date = _parse_date(row[headers_map["authorized_date"]])

        currency = account.currency
        if "currency" in headers_map and row.get(headers_map["currency"]):
            currency = str(row[headers_map["currency"]]).strip().upper() or currency

        amount_minor = parse_amount_to_minor(str(row[headers_map["amount"]]), currency)

        description = str(row[headers_map["description"]] or "").strip()
        normalized_description = normalize_text(description)

        provider_txn_id = None
        if "provider_txn_id" in headers_map and row.get(headers_map["provider_txn_id"]):
            provider_txn_id = str(row[headers_map["provider_txn_id"]]).strip() or None

        merchant_name = None
        if "merchant" in headers_map and row.get(headers_map["merchant"]):
            merchant_name = str(row[headers_map["merchant"]]).strip() or None

        dedup_hash = compute_dedup_hash(
            account_id=account_id,
            posted_date=posted_date,
            amount_minor=amount_minor,
            currency=currency,
            description=description,
        )

        merchant_id = None
        if merchant_name:
            mnorm = normalize_merchant_name(merchant_name)
            merchant = db.execute(select(Merchant).where(Merchant.normalized_name == mnorm)).scalar_one_or_none()
            if not merchant:
                merchant = Merchant(name=merchant_name.strip(), normalized_name=mnorm)
                db.add(merchant)
                db.flush()
            merchant_id = merchant.id

        # Apply rules (category) - uses merchant name and description
        match = match_category_rule(rules, merchant_name=merchant_name, description=description, amount_minor=amount_minor)
        category_id = match.category_id if match.matched else None
        if category_id is not None:
            stats["categorized"] += 1

        txn = Transaction(
            account_id=account_id,
            posted_date=posted_date,
            authorized_date=authorized_date,
            amount_minor=amount_minor,
            currency=currency,
            merchant_id=merchant_id,
            description=description,
            normalized_description=normalized_description,
            provider_txn_id=provider_txn_id,
            dedup_hash=dedup_hash,
            status="posted",
            category_id=category_id,
            import_job_id=job.id,
        )

        db.add(txn)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            # Re-open job in session after rollback
            job = db.get(ImportJob, job.id)
            stats["skipped_duplicates"] += 1
            continue

        log_audit(
            db,
            entity="transactions",
            entity_id=txn.id,
            action="create",
            before=None,
            after={
                "account_id": str(txn.account_id),
                "posted_date": txn.posted_date.isoformat(),
                "amount_minor": txn.amount_minor,
                "currency": txn.currency,
                "description": txn.description,
                "provider_txn_id": txn.provider_txn_id,
                "dedup_hash": txn.dedup_hash,
                "category_id": str(txn.category_id) if txn.category_id else None,
                "import_job_id": str(job.id),
            },
        )
        stats["created"] += 1

    job.status = "done"
    db.add(job)
    db.commit()
    db.refresh(job)
    return job, stats
