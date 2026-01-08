from typing import Optional, List
from pydantic import BaseModel

class CreditCardCreate(BaseModel):
    card_type: str
    annual_income: float
    employment_status: str
    company_name: Optional[str] = None
    position: Optional[str] = None

class CreditCardApplicationResponse(BaseModel):
    id: int
    card_type: str
    annual_income: Optional[float] = None
    employment_status: Optional[str] = None
    company_name: Optional[str] = None
    position: Optional[str] = None
    status: str
    created_at: str

    class Config:
        from_attributes = True

class CreditCardApplicationList(BaseModel):
    items: List[CreditCardApplicationResponse]
    page: int
    per_page: int
    total: int
    total_pages: int

class CreditCardPaymentRequest(BaseModel):
    user_id: int
    card_id: int
    amount: float

class CreditCardPaymentResponse(BaseModel):
    message: str
    new_balance_due: float

class CreditCardCashAdvanceRequest(BaseModel):
    card_id: int
    amount: float

class CreditCardCashAdvanceResponse(BaseModel):
    message: str
    new_balance_due: float
