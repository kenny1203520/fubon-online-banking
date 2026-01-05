from typing import Optional, List
from pydantic import BaseModel

# 生活繳費帳單響應
class UtilityBillResponse(BaseModel):
    id: int
    bill_type: str
    provider: str
    amount: float
    due_date: str
    status: str
    description: Optional[str] = None
    created_at: str
    paid_at: Optional[str] = None

    class Config:
        from_attributes = True

# 生活繳費帳單列表
class UtilityBillList(BaseModel):
    items: List[UtilityBillResponse]
    page: Optional[int] = None
    per_page: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None

# 繳費請求
class PayBillRequest(BaseModel):
    bill_id: int
    account_id: int
    amount: float
    payment_method: str = "bank_transfer"  # bank_transfer, credit_card

# 繳費響應
class PayBillResponse(BaseModel):
    transaction_id: int
    bill_id: int
    amount: float
    reference_number: str
    status: str
    created_at: str

    class Config:
        from_attributes = True

# 繳費記錄響應
class PaymentHistoryResponse(BaseModel):
    id: int
    bill_id: int
    amount: float
    payment_method: str
    reference_number: str
    created_at: str

    class Config:
        from_attributes = True

# 繳費記錄列表
class PaymentHistoryList(BaseModel):
    items: List[PaymentHistoryResponse]
    page: Optional[int] = None
    per_page: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None

# 獲取服務列表響應
class UtilityServiceResponse(BaseModel):
    service_type: str
    providers: List[str]
    description: str
