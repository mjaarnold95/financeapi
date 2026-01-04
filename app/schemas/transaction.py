import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field

class TransactionOut(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    posted_date: date
    authorized_date: date | None
    amount_minor: int
    currency: str
    merchant_id: uuid.UUID | None
    description: str
    normalized_description: str
    provider_txn_id: str | None
    dedup_hash: str
    status: str
    category_id: uuid.UUID | None
    import_job_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionList(BaseModel):
    items: list[TransactionOut]
    limit: int
    offset: int
    total: int
