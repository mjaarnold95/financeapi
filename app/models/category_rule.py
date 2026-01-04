import uuid
from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class CategoryRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "category_rules"

    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    merchant_contains: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_contains: Mapped[str | None] = mapped_column(Text, nullable=True)

    min_amount_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_amount_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)

    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    category = relationship("Category", back_populates="rules")
