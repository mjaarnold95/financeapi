import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)
    parent_id: uuid.UUID | None = None
    is_income: bool = False

class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None
    is_income: bool
    created_at: datetime

    class Config:
        from_attributes = True
