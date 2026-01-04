import uuid
from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDMixin, TimestampMixin

class Transaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    posted_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    authorized_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    merchant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_description: Mapped[str] = mapped_column(Text, nullable=False)

    provider_txn_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    dedup_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="posted")  # pending/posted/cleared/reconciled

    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    import_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("import_jobs.id"), nullable=True, index=True)

    account = relationship("Account", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    import_job = relationship("ImportJob", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_account_posted_date", "account_id", "posted_date"),
        Index("ix_transactions_account_dedup_hash", "account_id", "dedup_hash", unique=True),
    )
