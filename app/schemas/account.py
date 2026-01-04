import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class AccountCreate(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1, max_length=32)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    institution_id: uuid.UUID | None = None

class AccountOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    currency: str
    institution_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True
