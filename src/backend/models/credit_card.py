from sqlmodel import Field, SQLModel
from typing import Optional

class CreditCard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    card_number: str = Field(unique=True)
    limit_amount: float = Field(default=0.0)
    balance_due: float = Field(default=0.0)
    created_at: str

class CreditCardApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = None
    card_type: str
    annual_income: Optional[float] = None
    employment_status: Optional[str] = None
    company_name: Optional[str] = None
    position: Optional[str] = None
    status: str = Field(default="received")
    created_at: str

class CreditCardPayment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    card_id: int
    amount: float
    created_at: str
