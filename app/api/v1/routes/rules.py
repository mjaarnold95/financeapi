from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import CategoryRule
from app.schemas.rule import RuleCreate, RuleOut
from app.services.audit import log_audit

router = APIRouter()

@router.post("", response_model=RuleOut, status_code=201)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    rule = CategoryRule(**payload.model_dump())
    db.add(rule)
    db.flush()
    log_audit(db, entity="category_rules", entity_id=rule.id, action="create", before=None, after=payload.model_dump())
    db.commit()
    db.refresh(rule)
    return rule

@router.get("", response_model=list[RuleOut])
def list_rules(db: Session = Depends(get_db)):
    return db.execute(select(CategoryRule).order_by(CategoryRule.priority.asc())).scalars().all()
