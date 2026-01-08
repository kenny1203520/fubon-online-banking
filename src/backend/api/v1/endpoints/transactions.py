from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func, desc, or_
from datetime import datetime, timezone
from typing import Optional
import uuid
import random
import string

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

# 轉帳限額設定
TRANSFER_LIMITS = {
    "single_max": 1000000,  # 單筆最高100萬
    "daily_max": 3000000,   # 單日最高300萬
    "min_amount": 1,        # 最低金額1元
}

# 手續費設定
FEE_STRUCTURE = {
    "same_bank": 0,         # 本行轉帳免手續費
    "other_bank": 15,       # 跨行轉帳手續費15元
    "over_threshold": 10,   # 大額轉帳優惠手續費10元
    "threshold": 50000,     # 大額轉帳門檻5萬元
}

def generate_transaction_number() -> str:
    """生成唯一的交易流水號 (格式: TXN-YYYYMMDD-XXXXXXXX)"""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"TXN-{date_str}-{random_str}"

def calculate_transfer_fee(amount: float, is_same_bank: bool = True) -> float:
    """計算轉帳手續費"""
    if is_same_bank:
        return FEE_STRUCTURE["same_bank"]
    
    if amount >= FEE_STRUCTURE["threshold"]:
        return FEE_STRUCTURE["over_threshold"]
    
    return FEE_STRUCTURE["other_bank"]

def validate_daily_transfer_limit(session: Session, account_id: uuid.UUID, amount: float) -> bool:
    """驗證單日轉帳限額"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    # 查詢今日所有轉出交易
    statement = select(func.sum(Transaction.amount)).where(
        Transaction.account_id == account_id,
        Transaction.type == "transfer_out",
        Transaction.created_at >= today_start,
        Transaction.status == "completed"
    )
    today_total = session.exec(statement).first() or 0
    
    # 檢查是否超過單日限額
    if abs(today_total) + amount > TRANSFER_LIMITS["daily_max"]:
        return False
    
    return True

@router.get("/", response_model=TransactionList)
@router.post("/", response_model=TransactionList)
async def get_transactions(
    account_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    frm: Optional[str] = None,
    to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得交易列表 (Get transaction history)
    
    Parameters:
    - page: 頁碼 (page number)
    - per_page: 每頁項目數 (items per page, max 100)
    - account_id: 帳戶ID (account UUID, optional)
    - frm: 起始日期 (start date in ISO format)
    - to: 截止日期 (end date in ISO format)
    """
    # 驗證使用者身份
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required to get account details"
        )
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid user information"
        )
    
    # 轉換字串 UUID 為 UUID 物件
    try:
        account_uuid = uuid.UUID(account_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid account ID format'
        )
    
    offset = (page - 1) * per_page
    
    # 構建查詢
    query = select(Transaction)
    
    # 如果指定帳戶ID，查詢該帳戶的交易
    if account_id:
        try:
            account_uuid = uuid.UUID(account_id)
            # 查詢該帳戶的交易（包含轉出和轉入）
            query = query.where(
                or_(
                    Transaction.account_id == account_uuid,
                    Transaction.related_account_id == account_uuid
                )
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid account ID format"
            )
    
    # 日期範圍篩選
    if frm:
        query = query.where(Transaction.created_at >= frm)
    if to:
        query = query.where(Transaction.created_at <= to)
    
    # 計算總數
    count_query = select(func.count()).select_from(Transaction)
    if account_id:
        account_uuid = uuid.UUID(account_id)
        count_query = count_query.where(
            or_(
                Transaction.account_id == account_uuid,
                Transaction.related_account_id == account_uuid
            )
        )
    total = session.scalar(count_query) or 0
    
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
    - from_account_id: 來源帳戶ID (source account UUID)
    - from_account_number: 來源帳號 (source account number)
    - to_account_number: 目標帳號 (destination account number)
    - amount: 轉帳金額 (transfer amount)
    - currency: 貨幣類型 (currency type, e.g., TWD)
    - description: 備註 (description, optional)
    - show_desc_both: 雙方皆顯示備註 (show description to both parties)
    - password: 交易密碼 (transaction password, optional)
    - transfer_type: 轉帳類型 (transfer type, e.g., instant scheduled)
    
    Features:
    - 支援帳號或帳戶ID轉帳
    - 自動計算手續費
    - 驗證單日轉帳限額
    - 驗證帳戶狀態和餘額
    - 產生交易流水號
    """
    
    # ==================== 1. 驗證輸入參數 ====================
    if not request.from_account_id and not request.from_account_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請提供來源帳戶ID及帳號"
        )
    
    if not request.to_account_number or not request.to_account_number.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請提供目標帳戶帳號"
        )
    
    # 驗證金額
    if request.amount < TRANSFER_LIMITS["min_amount"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"轉帳金額不可低於 {TRANSFER_LIMITS['min_amount']} 元"
        )
    
    if request.amount > TRANSFER_LIMITS["single_max"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"單筆轉帳金額不可超過 {TRANSFER_LIMITS['single_max']:,} 元"
        )
    
    # ==================== 2. 取得來源帳戶 ====================
    if request.from_account_id:
        src_account = session.get(Account, request.from_account_id)
    else:
        statement = select(Account).where(Account.account_number == request.from_account_number)
        src_account = session.exec(statement).first()
    
    if not src_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="來源帳戶不存在"
        )
    
    # 驗證來源帳戶所有權
    if src_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限操作此帳戶"
        )
    
    # 驗證來源帳戶狀態
    if src_account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"來源帳戶狀態異常（{src_account.status}），無法進行轉帳"
        )
    
    # ==================== 3. 取得目標帳戶 ====================
    statement = select(Account).where(Account.account_number == request.to_account_number)
    dst_account = session.exec(statement).first()
    
    if not dst_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目標帳戶不存在"
        )
    
    # 驗證目標帳戶狀態
    if dst_account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"目標帳戶狀態異常（{dst_account.status}），無法接收轉帳"
        )
    
    # 驗證不可轉給自己
    if src_account.id == dst_account.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不可轉帳至相同帳戶"
        )
    
    # ==================== 4. 計算手續費 ====================
    # 判斷是否為本行轉帳（簡化版：檢查帳號前3碼是否相同）
    is_same_bank = (
        src_account.account_number[:3] == dst_account.account_number[:3]
    )
    fee = calculate_transfer_fee(request.amount, is_same_bank)
    total_amount = request.amount + fee
    
    # ==================== 5. 驗證餘額 ====================
    if src_account.balance < total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"餘額不足。可用餘額: {src_account.balance:,.2f} 元，需要: {total_amount:,.2f} 元（含手續費 {fee} 元）"
        )
    
    # ==================== 6. 驗證單日轉帳限額 ====================
    if not validate_daily_transfer_limit(session, src_account.id, request.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"已超過單日轉帳限額 {TRANSFER_LIMITS['daily_max']:,} 元"
        )
    
    # ==================== 7. 執行轉帳 ====================
    now = datetime.now(timezone.utc).isoformat()
    
    # 生成交易流水號（確保唯一性）
    while True:
        transaction_number = generate_transaction_number()
        existing = session.exec(
            select(Transaction).where(Transaction.transaction_number == transaction_number)
        ).first()
        if not existing:
            break
    
    try:
        # 更新帳戶餘額
        src_account.balance -= total_amount
        dst_account.balance += request.amount
        
        # 建立來源帳戶交易記錄（轉出）
        src_transaction = Transaction(
            transaction_number=transaction_number,
            account_id=src_account.id,
            account_number=src_account.account_number,
            type="transfer_out",
            amount=-request.amount,  # 負數表示轉出
            currency="TWD",
            fee=fee,
            related_account_id=dst_account.id,
            related_account_number=dst_account.account_number,
            status="completed",
            description=request.description or f"轉帳至 {dst_account.account_number} ({dst_account.full_name})",
            created_at=now
        )
        
        # 建立目標帳戶交易記錄（轉入）
        dst_transaction = Transaction(
            transaction_number=transaction_number,
            account_id=dst_account.id,
            account_number=dst_account.account_number,
            type="transfer_in",
            amount=request.amount,  # 正數表示轉入
            currency="TWD",
            fee=0,  # 收款方不收手續費
            related_account_id=src_account.id,
            related_account_number=src_account.account_number,
            status="completed",
            description=request.description or f"來自 {src_account.account_number} ({src_account.full_name}) 的轉帳",
            created_at=now
        )
        
        # 提交所有變更
        session.add(src_account)
        session.add(dst_account)
        session.add(src_transaction)
        session.add(dst_transaction)
        session.commit()
        session.refresh(src_transaction)
        
        # ==================== 8. 返回轉帳結果 ====================
        return TransferResponse(
            transaction_id=src_transaction.id,
            transaction_number=transaction_number,
            from_account_number=src_account.account_number,
            to_account_number=dst_account.account_number,
            amount=request.amount,
            currency="TWD",
            fee=fee,
            total_amount=total_amount,
            status="completed",
            created_at=now,
            message=f"轉帳成功！交易流水號: {transaction_number}"
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"轉帳處理失敗: {str(e)}"
        )

@router.post("/exchange", response_model=ExchangeResponse)
async def exchange(
    request: ExchangeRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    換匯交易 (Currency exchange)
    
    Parameters:
    - from_account: 來源帳戶ID (source account ID - 台幣帳戶)
    - to_account: 目標帳戶ID (target account ID - 外幣帳戶)
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
    
    # 取得來源帳戶（台幣帳戶）
    from_account = session.get(Account, request.from_account)
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    # 驗證來源帳戶是否屬於當前用戶
    if from_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this account"
        )
    
    # 驗證來源帳戶狀態
    if from_account.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source account is {from_account.status}"
        )
    
    # 驗證來源帳戶幣種
    if from_account.currency != request.from_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source account currency is {from_account.currency}, not {request.from_currency}"
        )
    
    # 取得目標帳戶（外幣帳戶）
    to_account = session.get(Account, request.to_account)
    if not to_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target account not found"
        )
    
    # 驗證目標帳戶是否屬於當前用戶
    if to_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access target account"
        )
    
    # 驗證目標帳戶必須是外幣帳戶
    if to_account.account_type != 'foreign_currency':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target account must be a foreign currency account"
        )
    
    # 驗證目標帳戶狀態
    if to_account.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target account is {to_account.status}"
        )
    
    # 驗證目標帳戶幣種
    if to_account.currency != request.to_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target account currency is {to_account.currency}, not {request.to_currency}"
        )
    
    # 驗證來源帳戶餘額
    if from_account.balance < request.amount:
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
    transaction_number = generate_transaction_number()
    
    # 更新來源帳戶餘額（扣款）
    from_account.balance -= request.amount
    
    # 更新目標帳戶餘額（入款）
    to_account.balance += to_amount
    
    # 建立來源帳戶的交易記錄（換匯扣款）
    from_transaction = Transaction(
        transaction_number=transaction_number + "-OUT",
        account_id=request.from_account,
        account_number=from_account.account_number,
        type="exchange",
        amount=-request.amount,  # 負數表示扣款
        currency=request.from_currency,
        related_account_id=request.to_account,
        related_account_number=to_account.account_number,
        status="completed",
        description=request.description or f"換匯 {request.from_currency} {request.amount:.2f} 至 {request.to_currency} {to_amount:.2f}",
        created_at=now
    )
    
    # 建立目標帳戶的交易記錄（換匯入款）
    to_transaction = Transaction(
        transaction_number=transaction_number + "-IN",
        account_id=request.to_account,
        account_number=to_account.account_number,
        type="exchange",
        amount=to_amount,  # 正數表示入款
        currency=request.to_currency,
        related_account_id=request.from_account,
        related_account_number=from_account.account_number,
        status="completed",
        description=request.description or f"收到換匯 {request.from_currency} {request.amount:.2f} 轉入 {request.to_currency} {to_amount:.2f}",
        created_at=now
    )
    
    session.add(from_account)
    session.add(to_account)
    session.add(from_transaction)
    session.add(to_transaction)
    session.commit()
    session.refresh(from_transaction)
    
    return {
        "transaction_id": from_transaction.id,
        "from_account": request.from_account,
        "to_account": request.to_account,
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
