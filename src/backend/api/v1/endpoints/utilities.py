from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func, desc
from datetime import datetime, timezone
from typing import Optional
import uuid

from models.utility import UtilityBill, UtilityPayment
from models.account import Account
from models.transaction import Transaction
from models.user import User
from schemas.utility import (
    UtilityBillResponse, UtilityBillList, PayBillRequest, PayBillResponse,
    PaymentHistoryResponse, PaymentHistoryList, UtilityServiceResponse
)
from core.database import get_session
from core.auth import get_current_user

router = APIRouter()

# 生活繳費服務配置
UTILITY_SERVICES = [
    {
        "service_type": "water",
        "providers": ["自來水公司北區分處", "自來水公司中區分處", "自來水公司南區分處"],
        "description": "水費繳納"
    },
    {
        "service_type": "electricity",
        "providers": ["台灣電力公司"],
        "description": "電費繳納"
    },
    {
        "service_type": "gas",
        "providers": ["台灣中油", "台灣自來水公司"],
        "description": "瓦斯費繳納"
    },
    {
        "service_type": "phone",
        "providers": ["中華電信", "遠傳電信", "台灣大哥大"],
        "description": "電話費繳納"
    },
    {
        "service_type": "internet",
        "providers": ["中華電信", "遠傳電信", "台灣大哥大"],
        "description": "網路費繳納"
    },
    {
        "service_type": "insurance",
        "providers": ["國泰人壽", "南山人壽", "新光人壽"],
        "description": "保險費繳納"
    }
]

@router.get("/services", response_model=list)
async def get_utilities(
    current_user: User = Depends(get_current_user)
):
    """
    取得生活繳費服務列表 (Get utility payment services)
    
    返回所有可提供的繳費服務類型與供應商列表
    """
    return UTILITY_SERVICES

@router.get("/bills", response_model=UtilityBillList)
async def get_bills(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    status: Optional[str] = None,
    bill_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得使用者的繳費帳單 (Get user's utility bills)
    
    Parameters:
    - page: 頁碼 (page number)
    - per_page: 每頁項目數 (items per page)
    - status: 帳單狀態篩選 (bill status filter: pending, paid, overdue)
    - bill_type: 帳單類型篩選 (bill type filter)
    """
    offset = (page - 1) * per_page
    
    # 構建查詢
    query = select(UtilityBill).where(UtilityBill.user_id == current_user.id)
    
    # 狀態篩選
    if status:
        query = query.where(UtilityBill.status == status)
    
    # 類型篩選
    if bill_type:
        query = query.where(UtilityBill.bill_type == bill_type)
    
    # 計算總數
    total = session.scalar(
        select(func.count()).select_from(UtilityBill).where(UtilityBill.user_id == current_user.id)
    ) or 0
    
    # 分頁排序
    query = query.order_by(desc(UtilityBill.id)).offset(offset).limit(per_page)
    bills = session.exec(query).all()
    
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        "items": [UtilityBillResponse.from_orm(b) for b in bills],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    }

@router.post("/pay-bill", response_model=PayBillResponse)
async def pay_bill(
    request: PayBillRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    支付帳單 (Pay utility bill)
    
    Parameters:
    - bill_id: 帳單ID (bill ID)
    - account_id: 繳費帳戶ID (payment account ID)
    - amount: 繳費金額 (payment amount)
    - payment_method: 繳費方式 (payment method: bank_transfer, credit_card)
    """
    # 取得帳單
    bill = session.get(UtilityBill, request.bill_id)
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # 驗證帳單所有者
    if bill.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay this bill"
        )
    
    # 驗證帳單狀態
    if bill.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill has already been paid"
        )
    
    # 取得帳戶
    account = session.get(Account, request.account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # 驗證金額
    if request.amount <= 0 or request.amount > bill.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment amount"
        )
    
    # 驗證餘額
    if account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # 執行支付
    now = datetime.now(timezone.utc).isoformat()
    reference_number = str(uuid.uuid4())[:8].upper()
    
    # 更新帳戶餘額
    account.balance -= request.amount
    
    # 更新帳單狀態
    if request.amount >= bill.amount:
        bill.status = "paid"
        bill.paid_at = now
    
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    # 建立支付記錄
    payment = UtilityPayment(
        bill_id=request.bill_id,
        user_id=current_user.id,
        account_id=request.account_id,
        amount=request.amount,
        payment_method=request.payment_method,
        reference_number=reference_number,
        created_at=now
    )
    
    # 建立交易記錄
    transaction = Transaction(
        account_id=request.account_id,
        type="utility_payment",
        amount=-request.amount,
        currency="TWD",
        description=f"繳費: {bill.bill_type} - {bill.provider}",
        created_at=now
    )
    
    session.add(account)
    session.add(bill)
    session.add(payment)
    session.add(transaction)
    session.commit()
    session.refresh(payment)
    
    return {
        "transaction_id": payment.id,
        "bill_id": request.bill_id,
        "amount": request.amount,
        "reference_number": reference_number,
        "status": "success",
        "created_at": now
    }

@router.get("/history", response_model=PaymentHistoryList)
async def get_payment_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    bill_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得繳費記錄 (Get payment history)
    
    Parameters:
    - page: 頁碼 (page number)
    - per_page: 每頁項目數 (items per page)
    - bill_id: 帳單ID篩選 (bill ID filter, optional)
    """
    offset = (page - 1) * per_page
    
    # 構建查詢
    query = select(UtilityPayment).where(UtilityPayment.user_id == current_user.id)
    
    # 帳單篩選
    if bill_id:
        query = query.where(UtilityPayment.bill_id == bill_id)
    
    # 計算總數
    total = session.scalar(
        select(func.count()).select_from(UtilityPayment).where(UtilityPayment.user_id == current_user.id)
    ) or 0
    
    # 分頁排序
    query = query.order_by(desc(UtilityPayment.id)).offset(offset).limit(per_page)
    payments = session.exec(query).all()
    
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        "items": [PaymentHistoryResponse.from_orm(p) for p in payments],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    }
