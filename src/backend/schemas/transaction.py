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
    page: Optional[int] = None
    per_page: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None

class TransactionQuery(BaseModel):
    account_id: int
    frm: Optional[str] = None
    to: Optional[str] = None

class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float
    description: Optional[str] = None

class TransferResponse(BaseModel):
    transaction_id: int
    from_account: int
    to_account: int
    amount: float
    created_at: str

    class Config:
        from_attributes = True

class ExchangeRequest(BaseModel):
    from_account: int
    from_currency: str
    to_currency: str
    amount: float
    description: Optional[str] = None

class ExchangeResponse(BaseModel):
    transaction_id: int
    from_account: int
    to_account: int
    from_amount: float
    to_amount: float
    exchange_rate: float
    created_at: str

    class Config:
        from_attributes = True
