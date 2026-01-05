from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    type: str
    amount: float
    currency: str
    related_account: Optional[int] = None
    description: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

class TransactionList(BaseModel):
    items: List[TransactionResponse]

class TransactionQuery(BaseModel):
    account_id: int
    frm: Optional[str] = None
    to: Optional[str] = None
