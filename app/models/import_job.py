from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class ImportJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "import_jobs"

    source: Mapped[str] = mapped_column(String(32), nullable=False, default="csv")
    filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="created")  # created/processing/done/failed

    transactions = relationship("Transaction", back_populates="import_job")
