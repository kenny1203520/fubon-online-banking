from typing import Optional, List
from pydantic import BaseModel

class AccountCreate(BaseModel):
    full_name: str
    id_number: str
    email: Optional[str] = None
    initial_deposit: float

class AccountResponse(BaseModel):
    id: int
    full_name: str
    id_number: str
    email: Optional[str] = None
    balance: float
    status: str
    cashless_enabled: bool
    created_at: str

    class Config:
        from_attributes = True

class AccountList(BaseModel):
    items: List[AccountResponse]
    page: int
    per_page: int
    total: int
    total_pages: int

class BalanceRequest(BaseModel):
    account_id: int

class BalanceResponse(BaseModel):
    account_id: int
    balance: float
    cashless_enabled: bool

class CashlessRequest(BaseModel):
    account_id: int
    enabled: bool

class CashlessResponse(BaseModel):
    account_id: int
    cashless_enabled: bool
