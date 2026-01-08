from sqlmodel import Field, SQLModel
from typing import Optional
import uuid

class Account(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    account_number: str = Field(default="", unique=True, index=True)
    account_name: str = Field(default="")
    full_name: str
    id_number: str = Field(index=True)
    email: Optional[str] = None
    phone: str = Field(default="")
    address: str = Field(default="")
    account_type: str = Field(default="savings")
    balance: float = Field(default=0.0)
    status: str = Field(default="pending")
    cashless_enabled: int = Field(default=0)
    created_at: str
