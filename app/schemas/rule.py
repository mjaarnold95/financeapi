import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class RuleCreate(BaseModel):
    priority: int = 100
    merchant_contains: str | None = None
    description_contains: str | None = None
    min_amount_minor: int | None = None
    max_amount_minor: int | None = None
    category_id: uuid.UUID
    is_active: bool = True

class RuleOut(BaseModel):
    id: uuid.UUID
    priority: int
    merchant_contains: str | None
    description_contains: str | None
    min_amount_minor: int | None
    max_amount_minor: int | None
    category_id: uuid.UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
