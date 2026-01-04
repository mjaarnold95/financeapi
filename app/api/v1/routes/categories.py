from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryOut
from app.services.audit import log_audit

router = APIRouter()

@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    cat = Category(name=payload.name, parent_id=payload.parent_id, is_income=payload.is_income)
    db.add(cat)
    db.flush()
    log_audit(db, entity="categories", entity_id=cat.id, action="create", before=None, after=payload.model_dump())
    db.commit()
    db.refresh(cat)
    return cat

@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.execute(select(Category).order_by(Category.name.asc())).scalars().all()
