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
    currency: Optional[str] = 'TWD'  # 外幣帳戶時可為空（表示多幣種）
    initial_deposit: float = 0  # 外幣帳戶開戶時可為0

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
        allowed_types = ['savings', 'checking', 'fixed_deposit', 'foreign_currency', 'investment']
        if v not in allowed_types:
            raise ValueError(f'帳戶類型必須為：{", ".join(allowed_types)}')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str, info) -> str:
        """驗證幣種"""
        # 外幣帳戶的currency可以為空或None，表示支持多幣種
        if not v:
            return v
        allowed_currencies = ['TWD', 'USD', 'EUR', 'JPY', 'GBP', 'CNY', 'HKD', 'AUD', 'SGD', 'KRW']
        if v not in allowed_currencies:
            raise ValueError(f'幣種必須為：{", ".join(allowed_currencies)}')
        return v
    
    @field_validator('initial_deposit')
    @classmethod
    def validate_initial_deposit(cls, v: float, info) -> float:
        """驗證初始存款金額"""
        # 外幣帳戶開戶時可以不存款（初始存款為0）
        # 其他帳戶類型需要最少1000元
        data = info.data
        if data.get('account_type') != 'foreign_currency':
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
    currency: str
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
