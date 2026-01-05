from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func, desc
from datetime import datetime, timezone
from typing import Optional
import uuid

from models.transaction import Transaction
from models.account import Account
from models.user import User
from schemas.transaction import (
    TransactionResponse, TransactionList, TransferRequest, TransferResponse,
    ExchangeRequest, ExchangeResponse
)
from core.database import get_session
from core.auth import get_current_user

router = APIRouter()

# 模擬匯率（實務應該從外部 API 取得）
EXCHANGE_RATES = {
    ("TWD", "USD"): 0.031,
    ("USD", "TWD"): 32.5,
    ("TWD", "JPY"): 3.2,
    ("JPY", "TWD"): 0.31,
    ("TWD", "EUR"): 0.029,
    ("EUR", "TWD"): 34.5,
}

@router.get("/", response_model=TransactionList)
async def get_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    account_id: Optional[int] = None,
    frm: Optional[str] = None,
    to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得交易列表 (Get transaction history)
    
    Parameters:
    - page: 頁碼 (page number)
    - per_page: 每頁項目數 (items per page)
    - account_id: 帳戶ID (account ID, optional)
    - frm: 起始日期 (start date in ISO format)
    - to: 截止日期 (end date in ISO format)
    """
    offset = (page - 1) * per_page
    
    # 構建查詢
    query = select(Transaction)
    
    # 如果指定帳戶ID，查詢該帳戶的交易
    if account_id:
        query = query.where(Transaction.account_id == account_id)
    
    # 日期範圍篩選
    if frm:
        query = query.where(Transaction.created_at >= frm)
    if to:
        query = query.where(Transaction.created_at <= to)
    
    # 計算總數
    total = session.scalar(
        select(func.count()).select_from(Transaction).where(
            (Transaction.account_id == account_id) if account_id else True
        )
    ) or 0
    
    # 分頁排序
    query = query.order_by(desc(Transaction.id)).offset(offset).limit(per_page)
    transactions = session.exec(query).all()
    
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        "items": [TransactionResponse.from_orm(t) for t in transactions],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    }

@router.post("/transfer", response_model=TransferResponse)
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    轉帳交易 (Transfer money between accounts)
    
    Parameters:
    - from_account: 來源帳戶ID (source account ID)
    - to_account: 目標帳戶ID (destination account ID)
    - amount: 轉帳金額 (transfer amount)
    - description: 備註 (description, optional)
    """
    # 驗證金額
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # 取得來源帳戶
    src_account = session.get(Account, request.from_account)
    if not src_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    # 取得目標帳戶
    dst_account = session.get(Account, request.to_account)
    if not dst_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found"
        )
    
    # 驗證餘額
    if src_account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # 執行轉帳
    now = datetime.now(timezone.utc).isoformat()
    
    # 更新帳戶餘額
    src_account.balance -= request.amount
    dst_account.balance += request.amount
    
    # 建立來源帳戶交易記錄
    src_transaction = Transaction(
        account_id=request.from_account,
        type="transfer_out",
        amount=-request.amount,
        currency="TWD",
        related_account=request.to_account,
        description=request.description or f"轉帳至帳戶 {request.to_account}",
        created_at=now
    )
    
    # 建立目標帳戶交易記錄
    dst_transaction = Transaction(
        account_id=request.to_account,
        type="transfer_in",
        amount=request.amount,
        currency="TWD",
        related_account=request.from_account,
        description=request.description or f"來自帳戶 {request.from_account} 的轉帳",
        created_at=now
    )
    
    session.add(src_account)
    session.add(dst_account)
    session.add(src_transaction)
    session.add(dst_transaction)
    session.commit()
    session.refresh(src_transaction)
    
    return {
        "transaction_id": src_transaction.id,
        "from_account": request.from_account,
        "to_account": request.to_account,
        "amount": request.amount,
        "created_at": now
    }

@router.post("/exchange", response_model=ExchangeResponse)
async def exchange(
    request: ExchangeRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    換匯交易 (Currency exchange)
    
    Parameters:
    - from_account: 來源帳戶ID (source account ID)
    - from_currency: 來源幣別 (source currency, e.g., TWD)
    - to_currency: 目標幣別 (target currency, e.g., USD)
    - amount: 換匯金額 (exchange amount)
    - description: 備註 (description, optional)
    """
    # 驗證金額
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # 驗證幣別
    if request.from_currency == request.to_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and target currencies must be different"
        )
    
    # 取得帳戶
    account = session.get(Account, request.from_account)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # 驗證餘額
    if account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # 取得匯率
    rate_key = (request.from_currency, request.to_currency)
    if rate_key not in EXCHANGE_RATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported currency pair: {request.from_currency} to {request.to_currency}"
        )
    
    exchange_rate = EXCHANGE_RATES[rate_key]
    to_amount = request.amount * exchange_rate
    
    # 執行換匯
    now = datetime.now(timezone.utc).isoformat()
    
    # 更新帳戶餘額
    account.balance -= request.amount
    
    # 建立交易記錄
    transaction = Transaction(
        account_id=request.from_account,
        type="exchange",
        amount=request.amount,
        currency=request.from_currency,
        description=request.description or f"換匯 {request.from_currency} {request.amount} 至 {request.to_currency} {to_amount:.2f}",
        created_at=now
    )
    
    session.add(account)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return {
        "transaction_id": transaction.id,
        "from_account": request.from_account,
        "to_account": request.from_account,
        "from_amount": request.amount,
        "to_amount": to_amount,
        "exchange_rate": exchange_rate,
        "created_at": now
    }

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得交易詳情 (Get transaction details)
    
    Parameters:
    - transaction_id: 交易ID (transaction ID)
    """
    transaction = session.get(Transaction, transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.from_orm(transaction)
