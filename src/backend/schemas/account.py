from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import uuid
import re

class AccountCreateRequest(BaseModel):
    full_name: str
    id_number: str
    email: Optional[EmailStr] = None
    phone: str
    address: str
    account_type: str = 'savings'
    initial_deposit: float

    @field_validator('id_number')
    @classmethod
    def validate_id_number(cls, v: str) -> str:
        """驗證台灣身分證號格式"""
        if not re.match(r'^[A-Z][12]\d{8}$', v):
            raise ValueError('身分證號格式不正確')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """驗證台灣手機號碼格式"""
        if not re.match(r'^09\d{8}$', v):
            raise ValueError('手機號碼格式不正確（應為09開頭的10碼數字）')
        return v
    
    @field_validator('account_type')
    @classmethod
    def validate_account_type(cls, v: str) -> str:
        """驗證帳戶類型"""
        allowed_types = ['savings', 'checking', 'fixed_deposit']
        if v not in allowed_types:
            raise ValueError(f'帳戶類型必須為：{", ".join(allowed_types)}')
        return v
    
    @field_validator('initial_deposit')
    @classmethod
    def validate_initial_deposit(cls, v: float) -> float:
        """驗證初始存款金額"""
        if v < 1000:
            raise ValueError('初始存款金額至少需要 1,000 元')
        if v > 10000000:
            raise ValueError('初始存款金額不可超過 10,000,000 元')
        return v

class AccountResponse(BaseModel):
    id: uuid.UUID
    account_number: str
    account_name: str
    full_name: str
    id_number: str
    email: Optional[str] = None
    phone: str
    address: str
    account_type: str
    balance: float
    status: str
    cashless_enabled: bool
    created_at: str

    class Config:
        from_attributes = True

class AccountCreateResponse(BaseModel):
    account_id: uuid.UUID
    account_number: str
    account_name: str
    status: str
    message: str

class AccountListResponse(BaseModel):
    items: List[AccountResponse]
    page: int
    per_page: int
    total: int
    total_pages: int

class BalanceResponse(BaseModel):
    account_id: uuid.UUID
    balance: float
    cashless_enabled: bool

class BalanceRequest(BaseModel):
    account_id: uuid.UUID

class CashlessRequest(BaseModel):
    account_id: uuid.UUID
    enabled: bool

class CashlessResponse(BaseModel):
    account_id: uuid.UUID
    cashless_enabled: bool
