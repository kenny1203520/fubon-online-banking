from sqlmodel import Field, SQLModel
from typing import Optional

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    loan_type: str = Field(default="personal")  # personal, mortgage, auto, business
    loan_amount: float
    interest_rate: float
    term_months: int
    monthly_payment: float
    remaining_balance: float
    next_payment_date: Optional[str] = None
    next_payment_amount: Optional[float] = None
    status: str = Field(default="pending")  # pending, approved, active, paid_off, rejected
    application_date: str
    approval_date: Optional[str] = None
    start_date: Optional[str] = None
    purpose: Optional[str] = None
    annual_income: Optional[float] = None
    employment_status: Optional[str] = None
    created_at: str

class LoanRepayment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    loan_id: int
    payment_date: str
    amount: float
    principal: float
    interest: float
    remaining_balance: float
    payment_method: str = Field(default="account")
    created_at: str
