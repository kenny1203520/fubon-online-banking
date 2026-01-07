from typing import Optional, List
from pydantic import BaseModel

class LoanApplyRequest(BaseModel):
    product_id: Optional[int] = None
    loan_amount: float
    term_months: int
    purpose: str
    employment_status: str
    annual_income: float
    company_name: Optional[str] = None
    years_employed: Optional[int] = None
    has_collateral: bool = False
    collateral_description: Optional[str] = None

class LoanApplyResponse(BaseModel):
    application_id: int
    status: str
    message: str

class LoanCalculateRequest(BaseModel):
    amount: float
    interest_rate: float
    term_months: int

class LoanCalculateResponse(BaseModel):
    loan_amount: float
    interest_rate: float
    term_months: int
    monthly_payment: float
    total_payment: float
    total_interest: float

class LoanResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    loan_type: str
    loan_amount: float
    interest_rate: float
    term_months: int
    monthly_payment: float
    remaining_balance: float
    next_payment_date: Optional[str] = None
    next_payment_amount: Optional[float] = None
    status: str
    application_date: str
    approval_date: Optional[str] = None
    start_date: Optional[str] = None

    class Config:
        from_attributes = True

class LoanListResponse(BaseModel):
    items: List[LoanResponse]
    total: int

class RepaymentScheduleItem(BaseModel):
    payment_number: int
    payment_date: str
    principal: float
    interest: float
    total_payment: float
    remaining_balance: float
    status: str

class RepaymentHistoryResponse(BaseModel):
    id: int
    loan_id: int
    payment_date: str
    amount: float
    principal: float
    interest: float
    remaining_balance: float
    payment_method: str

    class Config:
        from_attributes = True

class RepaymentRequest(BaseModel):
    loan_id: int
    amount: float
    payment_method: str = "account"

class RepaymentResponse(BaseModel):
    message: str
    remaining_balance: float
    next_payment_date: Optional[str] = None
    next_payment_amount: Optional[float] = None
