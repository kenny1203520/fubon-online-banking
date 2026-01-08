from typing import List, Optional
from pydantic import BaseModel
import uuid


class DashboardSummary(BaseModel):
    total_assets: float
    total_liabilities: float
    net_worth: float
    accounts_count: int
    cards_count: int
    last_updated: str


class AccountSummary(BaseModel):
    id: Optional[uuid.UUID]
    account_name: str
    account_type: str
    balance: float
    currency: str = "TWD"


class RecentTransaction(BaseModel):
    id: int
    type: str
    amount: float
    description: Optional[str] = None
    date: str
    account_name: str


class CreditCardSummary(BaseModel):
    id: int
    card_name: str
    card_number: str
    current_balance: float
    available_credit: float
    due_date: Optional[str] = None
    minimum_payment: Optional[float] = None


class InvestmentSummary(BaseModel):
    total_value: float
    total_cost: float
    total_gain: float
    gain_percentage: float
    holdings_count: int


class Notification(BaseModel):
    id: int
    type: str # info | warning | error | success
    title: str
    message: str
    read: bool = False
    created_at: str


class DashboardData(BaseModel):
    summary: DashboardSummary
    accounts: List[AccountSummary]
    recent_transactions: List[RecentTransaction]
    cards: List[CreditCardSummary]
    investment: InvestmentSummary
    notifications: List[Notification]
