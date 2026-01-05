from sqlmodel import Field, SQLModel
from typing import Optional

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    id_number: str
    email: Optional[str] = None
    balance: float = Field(default=0.0)
    status: str = Field(default="pending")
    cashless_enabled: int = Field(default=0)
    created_at: str
