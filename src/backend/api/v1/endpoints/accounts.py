from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func
from datetime import datetime, timezone
from typing import Optional

from models.account import Account
from models.transaction import Transaction
from models.user import User
from schemas.account import (
    AccountCreate, AccountResponse, AccountList, BalanceRequest, BalanceResponse,
    CashlessRequest, CashlessResponse
)
from schemas.transaction import TransactionList, TransactionResponse
from schemas.credit_card import TransferRequest, TransferResponse
from core.database import get_session
from core.auth import get_current_user

router = APIRouter()

@router.post('/open', status_code=status.HTTP_201_CREATED)
async def open_account(request: AccountCreate, session: Session = Depends(get_session)):
    """
    Open a new account (申請新帳戶)  
    The account will be created with 'pending' status and requires approval.  
    (建立的帳戶將處於「待審核」狀態，需經過審核。)  
    Parameters:
    - full_name: Full name of the account holder (帳戶持有人全名)
    - id_number: Identification number (身分證號)
    """
    account = Account(
        full_name=request.full_name,
        id_number=request.id_number,
        email=request.email,
        balance=request.initial_deposit,
        status='pending',
        created_at=datetime.now(timezone.utc).isoformat()
    ) # 創建帳戶並設置初始狀態為「待審核」
    session.add(account) # 將帳戶加入資料庫會話
    session.commit() # 提交變更以保存帳戶
    session.refresh(account) # 重新整理以獲取自動生成的ID等資訊
    
    return {
        'account_id': account.id,
        'status': 'pending',
        'message': '申請已建立，等待審核'
    } # 返回帳戶ID和狀態訊息

@router.get('', response_model=AccountList)
async def list_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all accounts with pagination. (分頁列出所有帳戶)  
    Parameters:
    - page: Page number (頁碼)
    - per_page: Number of accounts per page (每頁帳戶數)
    """
    offset = (page - 1) * per_page # 計算偏移量
    
    # Get total count of accounts
    total = session.exec(func.select(func.count(Account.id))).one()
    
    # Get accounts for the requested page
    statement = select(Account).order_by(Account.id.desc()).offset(offset).limit(per_page)
    accounts = session.exec(statement).all()

    # 計算總頁數
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        'items': [AccountResponse.from_orm(acc) for acc in accounts],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    } # 返回帳戶列表和分頁資訊

@router.post('/balance', response_model=BalanceResponse)
async def get_balance(
    request: BalanceRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get account balance (查詢帳戶餘額).  
    Parameters:
    - account_id: ID of the account (帳戶ID)
    """
    account = session.get(Account, request.account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        ) # 帳戶不存在，返回404錯誤
    
    return {
        'account_id': account.id,
        'balance': account.balance,
        'cashless_enabled': bool(account.cashless_enabled)
    } # 返回帳戶餘額和無現金提款狀態

@router.post('/transactions', response_model=TransactionList)
async def get_transactions(
    account_id: int,
    frm: Optional[str] = None,
    to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get account transactions with optional date range (查詢帳戶交易紀錄，可選擇日期範圍)  
    Parameters:
    - account_id: ID of the account (帳戶ID)
    - frm: Start date (inclusive) in ISO format (起始日期，包含)
    """
    query = select(Transaction).where(Transaction.account_id == account_id)
    
    if frm:
        query = query.where(Transaction.created_at >= frm)
    if to:
        query = query.where(Transaction.created_at <= to)
    
    query = query.order_by(Transaction.id.desc()).limit(100)
    transactions = session.exec(query).all()
    
    return {
        'items': [TransactionResponse.from_orm(t) for t in transactions]
    }

@router.post('/transfer', response_model=TransferResponse)
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Transfer money between accounts (帳戶間轉帳)  
    Parameters:
    - from_account: Source account ID (來源帳戶ID)
    - to_account: Destination account ID (目標帳戶ID)
    """
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='amount must be positive'
        )
    
    # Get accounts
    src_account = session.get(Account, request.from_account)
    dst_account = session.get(Account, request.to_account)
    
    if not src_account or not dst_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='source or destination account not found'
        )
    
    if src_account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='insufficient funds'
        )
    
    # Perform transfer
    src_account.balance -= request.amount
    dst_account.balance += request.amount
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Record transactions
    debit = Transaction(
        account_id=request.from_account,
        type='debit',
        amount=-request.amount,
        currency=request.currency,
        related_account=request.to_account,
        description='transfer out',
        created_at=now
    )
    
    credit = Transaction(
        account_id=request.to_account,
        type='credit',
        amount=request.amount,
        currency=request.currency,
        related_account=request.from_account,
        description='transfer in',
        created_at=now
    )
    
    session.add(debit)
    session.add(credit)
    session.commit()
    
    return {
        'message': 'transfer completed',
        'from_new_balance': src_account.balance,
        'to_new_balance': dst_account.balance
    }

@router.post('/cashless_withdraw', response_model=CashlessResponse)
async def cashless_withdraw(
    request: CashlessRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Enable/disable cashless withdrawal (啟用/停用無現金提款功能)  
    Parameters:
    - account_id: ID of the account (帳戶ID)
    - enabled: True to enable, False to disable (啟用為True，停用為False)
    """
    account = session.get(Account, request.account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        )
    
    account.cashless_enabled = 1 if request.enabled else 0
    session.add(account)
    session.commit()
    
    return {
        'account_id': account.id,
        'cashless_enabled': bool(account.cashless_enabled)
    }
