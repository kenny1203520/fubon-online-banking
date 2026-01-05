from sqlmodel import Field, SQLModel
from typing import Optional

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    amount: float
    status: str = Field(default="applied")
    created_at: str
