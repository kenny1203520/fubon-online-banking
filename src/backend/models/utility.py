from sqlmodel import Field, SQLModel
from typing import Optional

class UtilityBill(SQLModel, table=True):
    """生活繳費帳單模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    account_id: int = Field(foreign_key="account.id")
    bill_type: str  # 水費、電費、瓦斯費、電話費等
    provider: str  # 供應商名稱
    amount: float  # 繳費金額
    due_date: str  # 截止日期
    status: str = Field(default="pending")  # pending, paid, overdue
    description: Optional[str] = None
    created_at: str
    paid_at: Optional[str] = None

class UtilityPayment(SQLModel, table=True):
    """生活繳費記錄模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    bill_id: int = Field(foreign_key="utilitybill.id")
    user_id: int = Field(foreign_key="user.id")
    account_id: int = Field(foreign_key="account.id")
    amount: float
    payment_method: str  # bank_transfer, credit_card, cash
    reference_number: str  # 參考編號
    created_at: str
