from sqlmodel import Field, SQLModel
from typing import Optional

class InvestmentProduct(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    risk_level: str
    currency: str = "TWD"
    min_amount: float = 0.0
    description: Optional[str] = None
    created_at: Optional[str] = None
