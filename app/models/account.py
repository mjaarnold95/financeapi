import uuid
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class Account(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "accounts"

    institution_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # checking/credit/brokerage/loan/etc
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
