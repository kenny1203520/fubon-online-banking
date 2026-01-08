from sqlmodel import Field, SQLModel
from typing import Optional
import uuid

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_number: str = Field(default="", index=True) # 交易流水號
    account_id: uuid.UUID
    account_number: str
    type: str  # transfer_out, transfer_in, deposit, withdrawal, exchange, payment
    amount: float
    currency: str = Field(default="TWD")
    fee: float = Field(default=0.0)  # 手續費
    related_account_id: Optional[uuid.UUID] = None # 關聯帳戶 UUID
    related_account_number: Optional[str] = None # 關聯帳號
    status: str = Field(default="completed") # pending, completed, failed, cancelled
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
