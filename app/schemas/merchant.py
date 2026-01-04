import uuid
from datetime import datetime
from pydantic import BaseModel

class MerchantOut(BaseModel):
    id: uuid.UUID
    name: str
    normalized_name: str
    created_at: datetime

    class Config:
        from_attributes = True
