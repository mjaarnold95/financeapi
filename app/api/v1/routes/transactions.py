from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Transaction
from app.schemas.transaction import TransactionList, TransactionOut

router = APIRouter()

@router.get("", response_model=TransactionList)
def list_transactions(
    db: Session = Depends(get_db),
    account_id: str | None = None,
    start: date | None = None,
    end: date | None = None,
    min_amount_minor: int | None = None,
    max_amount_minor: int | None = None,
    category_id: str | None = None,
    merchant_id: str | None = None,
    status: str | None = None,
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = []
    if account_id:
        filters.append(Transaction.account_id == account_id)
    if start:
        filters.append(Transaction.posted_date >= start)
    if end:
        filters.append(Transaction.posted_date <= end)
    if min_amount_minor is not None:
        filters.append(Transaction.amount_minor >= min_amount_minor)
    if max_amount_minor is not None:
        filters.append(Transaction.amount_minor <= max_amount_minor)
    if category_id:
        filters.append(Transaction.category_id == category_id)
    if merchant_id:
        filters.append(Transaction.merchant_id == merchant_id)
    if status:
        filters.append(Transaction.status == status)
    if q:
        like = f"%{q.strip().upper()}%"
        filters.append(or_(Transaction.normalized_description.like(like), Transaction.description.ilike(f"%{q.strip()}%")))

    where = and_(*filters) if filters else None

    total = db.execute(select(func.count(Transaction.id)).where(where) if where is not None else select(func.count(Transaction.id))).scalar_one()
    stmt = select(Transaction)
    if where is not None:
        stmt = stmt.where(where)
    stmt = stmt.order_by(Transaction.posted_date.desc(), Transaction.created_at.desc()).limit(limit).offset(offset)
    items = db.execute(stmt).scalars().all()
    return TransactionList(items=items, limit=limit, offset=offset, total=total)
