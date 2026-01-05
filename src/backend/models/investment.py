from sqlmodel import Field, SQLModel
from typing import Optional

class Investment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int
    product_id: Optional[str] = None
    amount: float
    created_at: str
