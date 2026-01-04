from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Category, Transaction
from app.schemas.insights import MonthlyCashflowOut, MonthlySpendByCategoryOut

router = APIRouter()

def _month_expr():
    # YYYY-MM string
    return func.to_char(Transaction.posted_date, "YYYY-MM")

@router.get("/monthly-cashflow", response_model=MonthlyCashflowOut)
def monthly_cashflow(
    db: Session = Depends(get_db),
    account_id: str | None = None,
    start: date | None = None,
    end: date | None = None,
):
    month = _month_expr()
    income = func.sum(case((Transaction.amount_minor > 0, Transaction.amount_minor), else_=0))
    expense = func.sum(case((Transaction.amount_minor < 0, Transaction.amount_minor), else_=0))
    net = func.sum(Transaction.amount_minor)

    stmt = select(
        month.label("month"),
        func.coalesce(income, 0).label("income_minor"),
        func.coalesce(expense, 0).label("expense_minor"),
        func.coalesce(net, 0).label("net_minor"),
    )

    if account_id:
        stmt = stmt.where(Transaction.account_id == account_id)
    if start:
        stmt = stmt.where(Transaction.posted_date >= start)
    if end:
        stmt = stmt.where(Transaction.posted_date <= end)

    stmt = stmt.group_by(month).order_by(month.asc())

    rows = [
        {"month": r.month, "income_minor": int(r.income_minor), "expense_minor": int(r.expense_minor), "net_minor": int(r.net_minor)}
        for r in db.execute(stmt).all()
    ]
    return {"rows": rows}

@router.get("/monthly-spend-by-category", response_model=MonthlySpendByCategoryOut)
def monthly_spend_by_category(
    db: Session = Depends(get_db),
    account_id: str | None = None,
    start: date | None = None,
    end: date | None = None,
    include_uncategorized: bool = Query(default=True),
):
    month = _month_expr()
    spend = func.sum(case((Transaction.amount_minor < 0, Transaction.amount_minor), else_=0))

    stmt = (
        select(
            month.label("month"),
            Transaction.category_id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(spend, 0).label("spend_minor"),
        )
        .select_from(Transaction)
        .outerjoin(Category, Category.id == Transaction.category_id)
    )

    if account_id:
        stmt = stmt.where(Transaction.account_id == account_id)
    if start:
        stmt = stmt.where(Transaction.posted_date >= start)
    if end:
        stmt = stmt.where(Transaction.posted_date <= end)

    if not include_uncategorized:
        stmt = stmt.where(Transaction.category_id.is_not(None))

    stmt = stmt.group_by(month, Transaction.category_id, Category.name).order_by(month.asc(), func.coalesce(Category.name, "").asc())

    rows = []
    for r in db.execute(stmt).all():
        rows.append(
            {
                "month": r.month,
                "category_id": str(r.category_id) if r.category_id else None,
                "category_name": r.category_name,
                "spend_minor": int(r.spend_minor),
            }
        )
    return {"rows": rows}
