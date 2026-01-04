"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_income", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_categories_name", "categories", ["name"])

    op.create_table(
        "merchants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("normalized_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_merchants_name", "merchants", ["name"])
    op.create_index("ix_merchants_normalized_name", "merchants", ["normalized_name"])

    op.create_table(
        "import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="csv"),
        sa.Column("filename", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "category_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("merchant_contains", sa.Text(), nullable=True),
        sa.Column("description_contains", sa.Text(), nullable=True),
        sa.Column("min_amount_minor", sa.Integer(), nullable=True),
        sa.Column("max_amount_minor", sa.Integer(), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_category_rules_category_id", "category_rules", ["category_id"])

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("posted_date", sa.Date(), nullable=False),
        sa.Column("authorized_date", sa.Date(), nullable=True),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("normalized_description", sa.Text(), nullable=False),
        sa.Column("provider_txn_id", sa.Text(), nullable=True),
        sa.Column("dedup_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="posted"),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("import_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["import_job_id"], ["import_jobs.id"]),
    )
    op.create_index("ix_transactions_account_id", "transactions", ["account_id"])
    op.create_index("ix_transactions_posted_date", "transactions", ["posted_date"])
    op.create_index("ix_transactions_merchant_id", "transactions", ["merchant_id"])
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_import_job_id", "transactions", ["import_job_id"])
    op.create_index("ix_transactions_account_posted_date", "transactions", ["account_id", "posted_date"])
    op.create_index("ix_transactions_account_dedup_hash", "transactions", ["account_id", "dedup_hash"], unique=True)

    # provider_txn_id unique per account when present (partial unique index)
    op.create_index(
        "ux_transactions_account_provider_txn_id_not_null",
        "transactions",
        ["account_id", "provider_txn_id"],
        unique=True,
        postgresql_where=sa.text("provider_txn_id IS NOT NULL"),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("entity", sa.String(length=64), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("before", sa.JSON(), nullable=True),
        sa.Column("after", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_log_entity_id", "audit_log", ["entity_id"])

def downgrade() -> None:
    op.drop_index("ix_audit_log_entity_id", table_name="audit_log")
    op.drop_table("audit_log")

    op.drop_index("ux_transactions_account_provider_txn_id_not_null", table_name="transactions")
    op.drop_index("ix_transactions_account_dedup_hash", table_name="transactions")
    op.drop_index("ix_transactions_account_posted_date", table_name="transactions")
    op.drop_index("ix_transactions_import_job_id", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_index("ix_transactions_merchant_id", table_name="transactions")
    op.drop_index("ix_transactions_posted_date", table_name="transactions")
    op.drop_index("ix_transactions_account_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_category_rules_category_id", table_name="category_rules")
    op.drop_table("category_rules")

    op.drop_table("import_jobs")

    op.drop_index("ix_merchants_normalized_name", table_name="merchants")
    op.drop_constraint("uq_merchants_name", "merchants", type_="unique")
    op.drop_table("merchants")

    op.drop_constraint("uq_categories_name", "categories", type_="unique")
    op.drop_table("categories")

    op.drop_table("accounts")
