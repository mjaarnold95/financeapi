import uuid
from datetime import datetime
from pydantic import BaseModel

class ImportJobOut(BaseModel):
    id: uuid.UUID
    source: str
    filename: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ImportSummary(BaseModel):
    job: ImportJobOut
    total_rows: int
    created: int
    skipped_duplicates: int
    categorized: int
