from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func
from datetime import datetime, timezone

from models.credit_card import CreditCard, CreditCardApplication, CreditCardPayment
from models.account import Account
from models.transaction import Transaction
from schemas.credit_card import (
    CreditCardCreate, CreditCardApplicationResponse, CreditCardApplicationList,
    CreditCardPaymentRequest, CreditCardPaymentResponse,
    CreditCardCashAdvanceRequest, CreditCardCashAdvanceResponse
)
from core.database import get_session

router = APIRouter()

@router.post('/apply', status_code=status.HTTP_201_CREATED)
async def apply_creditcard(request: CreditCardCreate, session: Session = Depends(get_session)):
    """Apply for a credit card."""
    application = CreditCardApplication(
        full_name=request.full_name,
        id_number=request.id_number,
        annual_income=request.annual_income,
        card_type=request.card_type,
        status='received',
        created_at=datetime.now(timezone.utc).isoformat()
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    
    return {
        'application_id': application.id,
        'status': 'received',
        'message': '信用卡申請已收到'
    }

@router.get('', response_model=CreditCardApplicationList)
async def list_creditcards(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    """List all credit card applications with pagination."""
    offset = (page - 1) * per_page
    
    # Get total count
    total = session.exec(func.select(func.count(CreditCardApplication.id))).one()
    
    # Get applications
    statement = (
        select(CreditCardApplication)
        .order_by(CreditCardApplication.id.desc())
        .offset(offset)
        .limit(per_page)
    )
    applications = session.exec(statement).all()
    
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        'items': [CreditCardApplicationResponse.from_orm(app) for app in applications],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    }

@router.post('/pay', response_model=CreditCardPaymentResponse)
async def creditcard_pay(request: CreditCardPaymentRequest, session: Session = Depends(get_session)):
    """Make a credit card payment."""
    card = session.get(CreditCard, request.card_id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='card not found'
        )
    
    new_due = max(0.0, card.balance_due - request.amount)
    now = datetime.now(timezone.utc).isoformat()
    
    # Record payment
    payment = CreditCardPayment(
        card_id=request.card_id,
        amount=request.amount,
        created_at=now
    )
    
    card.balance_due = new_due
    session.add(payment)
    session.add(card)
    session.commit()
    
    return {
        'message': 'payment recorded',
        'new_balance_due': new_due
    }

@router.post('/cash_advance', response_model=CreditCardCashAdvanceResponse)
async def creditcard_cash_advance(
    request: CreditCardCashAdvanceRequest,
    session: Session = Depends(get_session)
):
    """Process cash advance on credit card."""
    card = session.get(CreditCard, request.card_id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='card not found'
        )
    
    if card.balance_due + request.amount > card.limit_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='exceeds card limit'
        )
    
    new_due = card.balance_due + request.amount
    now = datetime.now(timezone.utc).isoformat()
    
    # Record transaction
    transaction = Transaction(
        account_id=None,
        type='cash_advance',
        amount=request.amount,
        currency='TWD',
        description=f'cash advance card {request.card_id}',
        created_at=now
    )
    
    card.balance_due = new_due
    session.add(transaction)
    session.add(card)
    session.commit()
    
    return {
        'message': 'cash advance processed',
        'new_balance_due': new_due
    }
