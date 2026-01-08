from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func, desc
from datetime import datetime, timezone
from typing import Optional
import random
import string
import uuid

from models.account import Account
from models.transaction import Transaction
from models.user import User
from schemas.account import (
    AccountCreateRequest, AccountResponse, AccountListResponse, BalanceResponse,
    CashlessRequest, CashlessResponse, AccountCreateResponse, BalanceRequest
)
from schemas.transaction import TransactionsRequest, TransactionList, TransactionResponse
from schemas.credit_card import TransferRequest, TransferResponse
from core.database import get_session
from core.auth import get_current_user

router = APIRouter()

def generate_account_number() -> str:
    """生成唯一的銀行帳號 (格式: 012-XXX-XXXXXX)"""
    # 銀行代碼 012
    bank_code = "012"
    # 分行代碼 (3位數字)
    branch_code = ''.join(random.choices(string.digits, k=3))
    # 帳號 (6位數字)
    account_digits = ''.join(random.choices(string.digits, k=6))
    return f"{bank_code}-{branch_code}-{account_digits}"

def generate_account_name(account_type: str) -> str:
    """根據帳戶類型生成帳戶名稱"""
    type_names = {
        'savings': '儲蓄帳戶',
        'checking': '支票帳戶',
        'fixed_deposit': '定期存款帳戶',
        'foreign_currency': '外幣帳戶'
    }
    return type_names.get(account_type, '一般帳戶')

@router.get('', name="顯示帳戶列表", status_code=status.HTTP_200_OK, response_model=AccountListResponse)
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
    - current_user: Authenticated user (認證使用者)
    - session: Database session (資料庫session)
    """
    offset = (page - 1) * per_page # 計算偏移量
    
    # Get total count of accounts
    total = session.exec(select(func.count()).where(Account.user_id == current_user.id)).first() or 0
    
    # Get accounts for the requested page
    statement = select(Account).where(Account.user_id == current_user.id).order_by(desc(Account.id)).offset(offset).limit(per_page)
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

@router.get('/{account_id}', name="顯示單一帳戶資訊", status_code=status.HTTP_200_OK, response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get details of a single account by ID. (根據ID獲取單一帳戶詳情)  

    Parameters:
    - account_id: ID of the account (帳戶ID)
    - current_user: Authenticated user (認證使用者)
    - session: Database session (資料庫session)
    """
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='authentication required to get account details'
        )
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid user information'
        )

    # 轉換字串 UUID 為 UUID 物件
    try:
        account_uuid = uuid.UUID(account_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid account ID format'
        )

    account = session.get(Account, account_uuid) # 取得帳戶資料
    
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        ) # 帳戶不存在或不屬於當前使用者，返回404錯誤
    
    if not account.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='invalid account data'
        ) # 帳戶資料無效，返回500錯誤
    
    return AccountResponse(
        id=account.id,
        account_number=account.account_number,
        account_name=account.account_name,
        full_name=account.full_name,
        id_number=account.id_number,
        email=account.email,
        phone=account.phone,
        address=account.address,
        account_type=account.account_type,
        balance=account.balance,
        status=account.status,
        cashless_enabled=bool(account.cashless_enabled),
        created_at=account.created_at
    ) # 返回帳戶詳情

@router.post('/open', name="申請新帳戶", status_code=status.HTTP_201_CREATED, response_model=AccountCreateResponse)
async def open_account(request: AccountCreateRequest, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Open a new account (申請新帳戶)  
    The account will be created with 'pending' status and requires approval.  
    (建立的帳戶將處於「待審核」狀態，需經過審核。)  
    
    NOTE: This endpoint does NOT require authentication to allow new customers to open accounts.
    
    Parameters:
    - full_name: Full name of the account holder (帳戶持有人全名)
    - id_number: Identification number (身分證號)
    - email: Email address (電子郵件)
    - phone: Phone number (手機號碼)
    - address: Address (地址)
    - account_type: Account type (帳戶類型: savings, checking, fixed_deposit, foreign_currency)
    - initial_deposit: Initial deposit amount (初始存款金額)
    """
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='authentication required to open account'
        )
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid user information'
        )

    # 檢查是否已經有相同身分證的帳戶
    existing = session.exec(
        select(Account).where(Account.id_number == request.id_number)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='此身分證號已有申請紀錄'
        )
    
    # 生成唯一的帳號
    while True:
        account_number = generate_account_number()
        existing_number = session.exec(
            select(Account).where(Account.account_number == account_number)
        ).first()
        if not existing_number:
            break
    
    # 生成帳戶名稱
    account_name = generate_account_name(request.account_type)

    # 創建帳戶
    account = Account(
        user_id=current_user.id,
        account_number=account_number,
        account_name=account_name,
        full_name=request.full_name,
        id_number=request.id_number,
        email=request.email,
        phone=request.phone,
        address=request.address,
        account_type=request.account_type,
        balance=request.initial_deposit,
        status='pending',
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    session.add(account)
    session.commit()
    session.refresh(account)

    if not account.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='帳戶建立失敗，請稍後再試'
        )
    
    return AccountCreateResponse(
        account_id=account.id,
        account_number=account.account_number,
        account_name=account.account_name,
        status='pending',
        message='申請已建立，等待審核。預計 1-3 個工作天完成審核。'
    )

@router.post('/balance', name="查詢帳戶餘額", response_model=BalanceResponse)
async def get_balance(
    request: BalanceRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get account balance (查詢帳戶餘額).  
    Parameters:
    - account_id: ID of the account (帳戶ID)
    - current_user: Authenticated user (認證使用者)
    - session: Database session (資料庫session)
    """
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='authentication required to get balance'
        )
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid user information'
        )

    account = session.get(Account, request.account_id) # 取得帳戶資料
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        ) # 帳戶不存在，返回404錯誤
    
    # 驗證帳戶是否屬於當前使用者
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='cannot access an account that does not belong to you'
        )
    
    return {
        'account_id': account.id,
        'balance': account.balance,
        'cashless_enabled': bool(account.cashless_enabled)
    } # 返回帳戶餘額和無現金提款狀態

@router.post('/transactions', name="查詢帳戶交易紀錄", response_model=TransactionList)
async def get_transactions(
    request: TransactionsRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    frm: Optional[str] = None,
    to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get account transactions with optional date range (查詢帳戶交易紀錄，可選擇日期範圍)  
    Parameters:
    - account_id: ID of the account (帳戶ID)
    - page: Page number (頁碼)
    - per_page: Number of transactions per page (每頁交易數)
    - frm: Start date (inclusive) in ISO format (起始日期，包含當天)
    - to: End date (inclusive) in ISO format (結束日期，包含當天)
    - current_user: Authenticated user (認證使用者)
    - session: Database session (資料庫session)
    """
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='authentication required to get transactions'
        )
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid user information'
        )
    
    offset = (page - 1) * per_page
    query = select(Transaction).where(Transaction.account_id == request.account_id)
    
    if frm:
        query = query.where(Transaction.created_at >= frm)
    if to:
        query = query.where(Transaction.created_at <= to)
    
    # 計算總數
    total = session.scalar(
        select(func.count()).select_from(Transaction).where(Transaction.account_id == request.account_id)
    ) or 0
    
    query = query.order_by(desc(Transaction.id)).offset(offset).limit(per_page)
    transactions = session.exec(query).all()
    
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        'items': [TransactionResponse(
            id=0 if t.id is None else t.id,
            transaction_number=t.transaction_number,
            account_id=t.account_id,
            account_number=t.account_number,
            type=t.type,
            amount=t.amount,
            currency=t.currency,
            related_account_id=t.related_account_id,
            related_account_number=t.related_account_number,
            status=t.status,
            description=t.description,
            created_at=t.created_at
            ) for t in transactions],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    }

@router.post('/transfer', name="帳戶間轉帳", response_model=TransferResponse)
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Transfer money between accounts (帳戶間轉帳)  
    Parameters:
    - request: TransferRequest object containing transfer details (轉帳請求物件)
    - current_user: Authenticated user (認證使用者)
    - session: Database session (資料庫session)
    """
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='authentication required to perform transfer'
        )
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid user information'
        )
    
    # 檢查來源和目標帳號是否提供
    if not request.from_account_number or not request.to_account_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Both from_account_number and to_account_number are required'
        )

    # 檢查轉帳金額是否正確
    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid transfer amount'
        )
    
    #  取得來源和目標帳戶
    src_account = session.get(Account, request.from_account_number)
    dst_account = session.get(Account, request.to_account_number)

    # 檢查帳戶是否存在    
    if not src_account or not dst_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Account not found'
        )
    
    if not src_account.id or not dst_account.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='invalid account data'
        )
    
    # 檢查帳戶是否屬於當前使用者
    if src_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='cannot transfer from an account that does not belong to you'
        )
    
    # 檢查來源帳戶餘額是否足夠
    if src_account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Insufficient funds in the source account'
        )
    
    # 執行轉帳
    src_account.balance -= request.amount
    dst_account.balance += request.amount
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Record transactions
    debit = Transaction(
        account_id=src_account.id,
        account_number=request.from_account_number,
        type='debit',
        amount=-request.amount,
        currency=request.currency,
        related_account_id=dst_account.id,
        related_account_number=request.to_account_number,
        description='transfer out',
        created_at=now
    )
    
    credit = Transaction(
        account_id=dst_account.id,
        account_number=request.to_account_number,
        type='credit',
        amount=request.amount,
        currency=request.currency,
        related_account_id=src_account.id,
        related_account_number=request.from_account_number,
        description='transfer in',
        created_at=now
    )
    
    session.add(debit)
    session.add(credit)
    session.commit()
    session.refresh(src_account)
    session.refresh(dst_account)
    
    return TransferResponse(
        message='Transfer completed successfully',
        from_new_balance=src_account.balance,
        to_new_balance=dst_account.balance
    )


@router.post('/cashless_withdraw', name="啟用/停用無現金提款功能", response_model=CashlessResponse)
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
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='authentication required to set cashless withdrawal'
        )

    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid user information'
        )

    account = session.get(Account, request.account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        )
    
    # 驗證帳戶是否屬於當前使用者
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='cannot modify an account that does not belong to you'
        )
    
    account.cashless_enabled = 1 if request.enabled else 0
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return {
        'account_id': account.id,
        'cashless_enabled': bool(account.cashless_enabled)
    }
