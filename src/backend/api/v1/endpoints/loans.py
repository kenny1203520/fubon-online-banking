from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import math

from models.loan import Loan, LoanRepayment
from models.user import User
from schemas.loan import (
    LoanApplyRequest, LoanApplyResponse, LoanCalculateRequest, LoanCalculateResponse,
    LoanResponse, LoanListResponse, RepaymentScheduleItem, RepaymentHistoryResponse,
    RepaymentRequest, RepaymentResponse
)
from core.database import get_session
from core.auth import get_current_user

router = APIRouter()

def calculate_monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """計算月付金額 (等額本息)"""
    if annual_rate == 0:
        return principal / months
    
    monthly_rate = annual_rate / 12 / 100
    payment = principal * (monthly_rate * math.pow(1 + monthly_rate, months)) / \
              (math.pow(1 + monthly_rate, months) - 1)
    return round(payment, 2)

@router.post('/calculate', response_model=LoanCalculateResponse)
async def calculate_loan(
    request: LoanCalculateRequest,
    session: Session = Depends(get_session)
):
    """
    貸款試算 (Calculate loan payment)
    Parameters:
    - amount: 貸款金額
    - interest_rate: 年利率 (%)
    - term_months: 貸款期限 (月)
    
    此端點不需要認證，任何人都可以使用
    """
    monthly_payment = calculate_monthly_payment(
        request.amount,
        request.interest_rate,
        request.term_months
    )
    
    total_payment = monthly_payment * request.term_months
    total_interest = total_payment - request.amount
    
    return {
        'loan_amount': request.amount,
        'interest_rate': request.interest_rate,
        'term_months': request.term_months,
        'monthly_payment': round(monthly_payment, 2),
        'total_payment': round(total_payment, 2),
        'total_interest': round(total_interest, 2)
    }

@router.post('/apply', status_code=status.HTTP_201_CREATED, response_model=LoanApplyResponse)
async def apply_loan(
    request: LoanApplyRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    申請貸款 (Apply for a loan)
    Parameters:
    - loan_amount: 貸款金額
    - term_months: 貸款期限 (月)
    - purpose: 貸款用途
    - employment_status: 就業狀態
    - annual_income: 年收入
    """
    # 確保使用者ID存在
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='user ID is None'
        )
    
    # 根據信用評分決定利率 (簡化版)
    interest_rate = 3.5  # 基礎利率
    if request.annual_income < 300000:
        interest_rate = 5.5
    elif request.annual_income < 600000:
        interest_rate = 4.5
    elif request.annual_income >= 1000000:
        interest_rate = 2.5
    
    if request.has_collateral:
        interest_rate -= 0.5  # 有擔保品降低利率
    
    # 計算月付金額
    monthly_payment = calculate_monthly_payment(
        request.loan_amount,
        interest_rate,
        request.term_months
    )
    
    now = datetime.now(timezone.utc)
    
    loan = Loan(
        user_id=current_user.id,
        product_id=request.product_id,
        product_name="個人信貸" if not request.product_id else None,
        loan_type="personal",
        loan_amount=request.loan_amount,
        interest_rate=interest_rate,
        term_months=request.term_months,
        monthly_payment=monthly_payment,
        remaining_balance=request.loan_amount,
        status='approved',  # 立刻核准
        application_date=now.isoformat(),
        purpose=request.purpose,
        annual_income=request.annual_income,
        employment_status=request.employment_status,
        created_at=now.isoformat()
    )
    
    session.add(loan)
    session.commit()
    session.refresh(loan)
    
    return {
        'application_id': loan.id,
        'status': 'approved',
        'message': f'恭喜！您的貸款申請已核准！利率：{interest_rate}%，月付金額：NT$ {monthly_payment:,.0f}'
    }

@router.get('', response_model=LoanListResponse)
async def get_my_loans(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得我的貸款列表 (Get my loans)
    """
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='user ID is None'
        )
    
    statement = select(Loan).where(Loan.user_id == current_user.id).order_by(Loan.id.desc())
    loans = session.exec(statement).all()
    
    return {
        'items': [LoanResponse.from_orm(loan) for loan in loans],
        'total': len(loans)
    }

@router.get('/{loan_id}', response_model=LoanResponse)
async def get_loan_detail(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得貸款詳情 (Get loan details)
    """
    loan = session.get(Loan, loan_id)
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Loan not found'
        )
    
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access this loan'
        )
    
    return LoanResponse.from_orm(loan)

@router.get('/{loan_id}/schedule', response_model=list[RepaymentScheduleItem])
async def get_repayment_schedule(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得還款計劃 (Get repayment schedule)
    """
    loan = session.get(Loan, loan_id)
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Loan not found'
        )
    
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized'
        )
    
    if loan.status not in ['active', 'approved']:
        return []
    
    # 生成還款計劃
    schedule = []
    remaining = loan.loan_amount
    monthly_rate = loan.interest_rate / 12 / 100
    
    start_date = datetime.fromisoformat(loan.start_date) if loan.start_date else datetime.now(timezone.utc)
    
    for i in range(1, loan.term_months + 1):
        interest = remaining * monthly_rate
        principal = loan.monthly_payment - interest
        remaining -= principal
        
        payment_date = start_date + relativedelta(months=i)
        
        schedule.append({
            'payment_number': i,
            'payment_date': payment_date.isoformat(),
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'total_payment': loan.monthly_payment,
            'remaining_balance': round(max(0, remaining), 2),
            'status': 'pending'
        })
    
    return schedule

@router.get('/{loan_id}/history', response_model=list[RepaymentHistoryResponse])
async def get_repayment_history(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    取得還款記錄 (Get repayment history)
    """
    loan = session.get(Loan, loan_id)
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Loan not found'
        )
    
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized'
        )
    
    statement = select(LoanRepayment).where(
        LoanRepayment.loan_id == loan_id
    ).order_by(LoanRepayment.payment_date.desc())
    
    repayments = session.exec(statement).all()
    
    return [RepaymentHistoryResponse.from_orm(r) for r in repayments]

@router.post('/repay', response_model=RepaymentResponse)
async def make_repayment(
    request: RepaymentRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    貸款還款 (Make loan repayment)
    """
    loan = session.get(Loan, request.loan_id)
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Loan not found'
        )
    
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized'
        )
    
    if loan.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Loan is not active'
        )
    
    # 計算本金和利息
    monthly_rate = loan.interest_rate / 12 / 100
    interest = loan.remaining_balance * monthly_rate
    principal = request.amount - interest
    
    new_balance = loan.remaining_balance - principal
    
    # 創建還款記錄
    now = datetime.now(timezone.utc)
    repayment = LoanRepayment(
        loan_id=request.loan_id,
        payment_date=now.isoformat(),
        amount=request.amount,
        principal=round(principal, 2),
        interest=round(interest, 2),
        remaining_balance=round(max(0, new_balance), 2),
        payment_method=request.payment_method,
        created_at=now.isoformat()
    )
    
    # 更新貸款餘額
    loan.remaining_balance = round(max(0, new_balance), 2)
    
    if loan.remaining_balance <= 0:
        loan.status = 'paid_off'
        loan.next_payment_date = None
        loan.next_payment_amount = None
    else:
        # 計算下次還款日期
        next_date = now + relativedelta(months=1)
        loan.next_payment_date = next_date.isoformat()
        loan.next_payment_amount = loan.monthly_payment
    
    session.add(repayment)
    session.add(loan)
    session.commit()
    
    return {
        'message': '還款成功' if loan.status != 'paid_off' else '貸款已全部清償！',
        'remaining_balance': loan.remaining_balance,
        'next_payment_date': loan.next_payment_date,
        'next_payment_amount': loan.next_payment_amount
    }
