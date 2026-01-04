from pydantic import BaseModel

class MonthlyCashflowRow(BaseModel):
    month: str  # YYYY-MM
    income_minor: int
    expense_minor: int
    net_minor: int

class MonthlyCashflowOut(BaseModel):
    rows: list[MonthlyCashflowRow]

class SpendByCategoryRow(BaseModel):
    month: str
    category_id: str | None
    category_name: str | None
    spend_minor: int  # negative sum (expenses)

class MonthlySpendByCategoryOut(BaseModel):
    rows: list[SpendByCategoryRow]
