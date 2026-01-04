from fastapi import APIRouter
from app.api.v1.routes import accounts, categories, transactions, rules, imports, insights

api_router = APIRouter()

api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(imports.router, prefix="/imports", tags=["imports"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
