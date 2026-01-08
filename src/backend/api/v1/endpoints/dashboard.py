from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func, desc, or_
from datetime import datetime, timezone
from typing import List, cast
import uuid

from core.database import get_session
from core.auth import get_current_user

from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.credit_card import CreditCard
from models.loan import Loan
from models.investment import Investment
from models.notification import Notification as NotificationModel

from schemas.dashboard import (
    DashboardData, DashboardSummary, AccountSummary, RecentTransaction,
    CreditCardSummary, InvestmentSummary, Notification
)

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_tx_type(t: str) -> str:
    if t in ("transfer_in", "transfer_out", "transfer"):
        return "transfer"
    if t in ("withdrawal", "utility_payment", "payment"):
        return "withdrawal"
    if t == "deposit":
        return "deposit"
    return t


def _ensure_user_notifications(session: Session, user: User):
    """若使用者尚無通知，建立一則歡迎通知"""
    if not user.id:
        return
    uid = cast(uuid.UUID, user.id)
    count_stmt = select(func.count()).select_from(NotificationModel).where(NotificationModel.user_id == uid)
    existing = session.exec(count_stmt).first() or 0
    if existing == 0:
        welcome = NotificationModel(
            user_id=uid,
            type="info",
            title="歡迎回來！",
            message="您的儀表板已就緒，開始管理您的資產吧。",
            read=False,
            created_at=_now_iso()
        )
        session.add(welcome)
        session.commit()


@router.get("/", response_model=DashboardData)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")

    # 帳戶
    accounts = session.exec(select(Account).where(Account.user_id == current_user.id)).all()
    account_ids = [a.id for a in accounts if a.id]

    accounts_summary = [
        AccountSummary(
            id=a.id, account_name=a.account_name, account_type=a.account_type,
            balance=a.balance, currency="TWD"
        ) for a in accounts
    ]

    # 最近交易（取使用者所有帳戶）
    # 避免 in_ 型別檢查問題，改用 or_
    tx_filter = or_(*[Transaction.account_id == acc_id for acc_id in account_ids]) if account_ids else None
    tx_query = select(Transaction)
    if tx_filter is not None:
        tx_query = tx_query.where(tx_filter)
    tx_query = tx_query.order_by(desc(Transaction.id)).limit(10)
    txs = session.exec(tx_query).all()
    # 構建帳戶名稱映射
    name_map = {str(a.id): a.account_name for a in accounts if a.id}
    recent_transactions = [
        RecentTransaction(
            id=t.id or 0,
            type=_map_tx_type(t.type),
            amount=t.amount,
            description=t.description,
            date=t.created_at,
            account_name=name_map.get(str(t.account_id), "")
        ) for t in txs
    ]

    # 信用卡
    cards = session.exec(select(CreditCard).where(CreditCard.user_id == 0)).all()  # 無法關聯UUID，先以0佔位
    cards_summary = [
        CreditCardSummary(
            id=c.id or 0,
            card_name="信用卡",
            card_number=c.card_number,
            current_balance=c.balance_due,
            available_credit=max(0.0, (c.limit_amount or 0.0) - (c.balance_due or 0.0)),
            due_date=None,
            minimum_payment=None
        ) for c in cards
    ]

    # 投資（簡化：金額總和）
    investments = session.exec(select(Investment)).all()
    total_inv = sum(i.amount for i in investments)
    inv_summary = InvestmentSummary(
        total_value=total_inv,
        total_cost=total_inv,
        total_gain=0.0,
        gain_percentage=0.0,
        holdings_count=len(investments)
    )

    # 負債：貸款餘額 + 信用卡未出帳
    loans = session.exec(select(Loan).where(Loan.user_id == current_user.id)).all()
    total_loan_balance = sum(l.remaining_balance for l in loans)
    total_card_due = sum((c.balance_due or 0.0) for c in cards)

    total_assets = sum(a.balance for a in accounts)
    total_liabilities = (total_loan_balance or 0.0) + (total_card_due or 0.0)
    summary = DashboardSummary(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        accounts_count=len(accounts),
        cards_count=len(cards),
        last_updated=_now_iso()
    )

    # 通知（資料庫）
    _ensure_user_notifications(session, current_user)
    notif_stmt = select(NotificationModel).where(NotificationModel.user_id == current_user.id).order_by(desc(NotificationModel.id))
    notif_models = session.exec(notif_stmt).all()
    notifications = [
        Notification(
            id=n.id or 0,
            type=n.type,
            title=n.title,
            message=n.message,
            read=bool(n.read),
            created_at=n.created_at
        ) for n in notif_models
    ]

    return DashboardData(
        summary=summary,
        accounts=accounts_summary,
        recent_transactions=recent_transactions,
        cards=cards_summary,
        investment=inv_summary,
        notifications=notifications
    )


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")

    accounts = session.exec(select(Account).where(Account.user_id == current_user.id)).all()
    loans = session.exec(select(Loan).where(Loan.user_id == current_user.id)).all()
    cards = session.exec(select(CreditCard).where(CreditCard.user_id == 0)).all()

    total_assets = sum(a.balance for a in accounts)
    total_loan_balance = sum(l.remaining_balance for l in loans)
    total_card_due = sum((c.balance_due or 0.0) for c in cards)
    total_liabilities = (total_loan_balance or 0.0) + (total_card_due or 0.0)

    return DashboardSummary(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        accounts_count=len(accounts),
        cards_count=len(cards),
        last_updated=_now_iso()
    )


@router.get("/accounts", response_model=List[AccountSummary])
async def get_accounts_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    accounts = session.exec(select(Account).where(Account.user_id == current_user.id)).all()
    return [
        AccountSummary(
            id=a.id, account_name=a.account_name, account_type=a.account_type,
            balance=a.balance, currency="TWD"
        ) for a in accounts
    ]


@router.get("/transactions/recent", response_model=List[RecentTransaction])
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    accounts = session.exec(select(Account).where(Account.user_id == current_user.id)).all()
    account_ids = [a.id for a in accounts if a.id]
    name_map = {str(a.id): a.account_name for a in accounts if a.id}
    tx_filter = or_(*[Transaction.account_id == acc_id for acc_id in account_ids]) if account_ids else None
    tx_query = select(Transaction)
    if tx_filter is not None:
        tx_query = tx_query.where(tx_filter)
    tx_query = tx_query.order_by(desc(Transaction.id)).limit(limit)
    txs = session.exec(tx_query).all()
    return [
        RecentTransaction(
            id=t.id or 0,
            type=_map_tx_type(t.type),
            amount=t.amount,
            description=t.description,
            date=t.created_at,
            account_name=name_map.get(str(t.account_id), "")
        ) for t in txs
    ]


@router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    _ensure_user_notifications(session, current_user)
    stmt = select(NotificationModel).where(NotificationModel.user_id == current_user.id).order_by(desc(NotificationModel.id))
    rows = session.exec(stmt).all()
    return [
        Notification(
            id=r.id or 0,
            type=r.type,
            title=r.title,
            message=r.message,
            read=bool(r.read),
            created_at=r.created_at
        ) for r in rows
    ]


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    notif = session.get(NotificationModel, notification_id)
    if not notif or notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="notification not found")
    notif.read = True
    session.add(notif)
    session.commit()
    return {"status": "ok"}


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    _ensure_user_notifications(session, current_user)
    stmt = select(NotificationModel).where(NotificationModel.user_id == current_user.id)
    rows = session.exec(stmt).all()
    for n in rows:
        n.read = True
        session.add(n)
    session.commit()
    return {"status": "ok"}
