from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Account
from app.schemas.account import AccountCreate, AccountOut
from app.services.audit import log_audit

router = APIRouter()

@router.post("", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    acct = Account(
        name=payload.name,
        type=payload.type,
        currency=payload.currency.upper(),
        institution_id=payload.institution_id,
    )
    db.add(acct)
    db.flush()
    log_audit(db, entity="accounts", entity_id=acct.id, action="create", before=None, after=payload.model_dump())
    db.commit()
    db.refresh(acct)
    return acct

@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.execute(select(Account).order_by(Account.created_at.desc())).scalars().all()

@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: str, db: Session = Depends(get_db)):
    acct = db.get(Account, account_id)
    if not acct:
        raise HTTPException(status_code=404, detail="account not found")
    return acct
