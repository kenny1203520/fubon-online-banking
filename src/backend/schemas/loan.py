from typing import Optional
from pydantic import BaseModel

class LoanApplyRequest(BaseModel):
    user_id: int
    amount: float

class LoanApplyResponse(BaseModel):
    loan_id: int
    status: str
    message: str

    class Config:
        from_attributes = True
