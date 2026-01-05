from sqlmodel import Field, SQLModel
from typing import Optional

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int
    type: str
    amount: float
    currency: str = Field(default="TWD")
    related_account: Optional[int] = None
    description: Optional[str] = None
    created_at: str
