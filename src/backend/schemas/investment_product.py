from pydantic import BaseModel
from typing import Optional, List

class InvestmentProductResponse(BaseModel):
    id: int
    name: str
    risk_level: str
    currency: str
    min_amount: float
    description: Optional[str]
    created_at: Optional[str]

    class Config:
        orm_mode = True

class InvestmentProductList(BaseModel):
    items: List[InvestmentProductResponse]
