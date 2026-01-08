from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

class TransactionResponse(BaseModel):
    id: int
    transaction_number: str
    account_id: int
    type: str
    amount: float
    currency: str
    fee: float = 0.0
    related_account: Optional[uuid.UUID] = None
    related_account_number: Optional[str] = None
    status: str
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionList(BaseModel):
    items: List[TransactionResponse]
    page: Optional[int] = None
    per_page: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None

class TransactionQuery(BaseModel):
    account_id: uuid.UUID
    frm: Optional[str] = None
    to: Optional[str] = None

class TransferRequest(BaseModel):
    from_account: Optional[uuid.UUID] = None  # 來源帳戶ID（擇一）
    from_account_number: Optional[str] = None  # 來源帳號（擇一）
    to_account: Optional[uuid.UUID] = None  # 目標帳戶ID（擇一）
    to_account_number: Optional[str] = None  # 目標帳號（擇一）
    amount: float = Field(gt=0, description="轉帳金額必須大於0")
    description: Optional[str] = Field(None, max_length=200)
    password: Optional[str] = None  # 交易密碼（可選）
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('轉帳金額必須大於0')
        if v > 1000000:
            raise ValueError('單筆轉帳金額不可超過100萬')
        return round(v, 2)  # 保留兩位小數
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_account_number": "012-123-456789",
                "to_account_number": "012-789-123456",
                "amount": 1000.0,
                "description": "還款"
            }
        }

class TransferResponse(BaseModel):
    transaction_number: str
    from_account: uuid.UUID
    from_account_number: str
    to_account: uuid.UUID
    to_account_number: str
    amount: float
    fee: float
    total_amount: float  # 含手續費的總金額
    status: str
    created_at: str
    message: str

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
