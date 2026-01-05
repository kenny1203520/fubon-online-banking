from typing import Optional, List
from pydantic import BaseModel

class InvestmentCreate(BaseModel):
    account_id: int
    product_id: str
    amount: float

class InvestmentResponse(BaseModel):
    id: int
    account_id: int
    product_id: Optional[str] = None
    amount: float
    created_at: str

    class Config:
        from_attributes = True

class InvestmentList(BaseModel):
    items: List[InvestmentResponse]

class InvestmentPurchaseRequest(BaseModel):
    account_id: int
    product_id: str
    amount: float

class InvestmentPurchaseResponse(BaseModel):
    message: str
    new_balance: float
