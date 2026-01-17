# FinanceAPI (MVP)

FastAPI + SQLAlchemy (sync) + psycopg v3 + Alembic, targeting **Python 3.12** and **PostgreSQL 16+**.

## Quickstart

1) Create a venv (Python 3.12):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

2) Set env vars (example):
```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/financeapi"
export APP_ENV="dev"
```

3) Run migrations:
```bash
alembic upgrade head
```

4) Start API:
```bash
uvicorn app.main:app --reload
```

Open docs:
- http://localhost:8000/docs

## CSV Import

Endpoint: `POST /api/v1/imports/csv?account_id=<uuid>`

CSV columns supported (case-insensitive, common aliases):
- posted_date: `posted_date`, `date`, `posted`
- amount: `amount`, `amt`, `amount_minor`, `cents`
- description: `description`, `memo`, `name`
- authorized_date: `authorized_date`, `auth_date` (optional)
- currency: `currency` (optional; defaults to account currency)
- provider_txn_id: `provider_txn_id`, `fitid`, `transaction_id` (optional)

Amount can be either:
- integer minor units (cents), e.g. `-1234`
- decimal major units, e.g. `-12.34` (will be converted using the account currency's minor exponent; USD=2)

## Notes

- Money is stored as **integer minor units** (`amount_minor BIGINT`).
- Sign convention: **expenses negative, income positive** (relative to account).
- Imports are **idempotent** via:
  - `UNIQUE(account_id, provider_txn_id)` when provider id exists
  - `UNIQUE(account_id, dedup_hash)` fallback hash

## Tests

```bash
pytest
```

The test suite includes:
- normalization & dedup hash stability
- rule matching logic
- CSV parsing + amount conversion
