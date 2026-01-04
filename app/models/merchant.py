from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class Merchant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "merchants"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    normalized_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)

    transactions = relationship("Transaction", back_populates="merchant")
