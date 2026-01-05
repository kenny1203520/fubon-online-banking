from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from typing import Optional

from models.investment import Investment
from models.account import Account
from models.transaction import Transaction
from schemas.investment import (
    InvestmentList, InvestmentResponse, InvestmentPurchaseRequest, InvestmentPurchaseResponse
)
from core.database import get_session

router = APIRouter()

@router.post('/query', response_model=InvestmentList)
async def query_investments(
    account_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    Query investments for an account or all investments (查詢帳戶或所有投資產品)  
    Parameters:
    - account_id: Optional account ID to filter investments (可選的帳戶ID，用於篩選投資)
    """
    if account_id:
        query = select(Investment).where(Investment.account_id == account_id)
    else:
        query = select(Investment).limit(100)
    
    query = query.order_by(Investment.id.desc())
    investments = session.exec(query).all()
    
    return {
        'items': [InvestmentResponse.from_orm(inv) for inv in investments]
    }

@router.post('/purchase', response_model=InvestmentPurchaseResponse)
async def purchase_investment(
    request: InvestmentPurchaseRequest,
    session: Session = Depends(get_session)
):
    """
    Purchase an investment product (購買投資產品)
    Parameters:
    - account_id: ID of the account making the purchase (購買投資的帳戶ID)
    - product_id: ID of the investment product (投資產品ID)
    - amount: Amount to invest (投資金額)
    """
    account = session.get(Account, request.account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        )
    
    if account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='insufficient funds'
        )
    
    # Deduct amount and record
    account.balance -= request.amount
    now = datetime.now(timezone.utc).isoformat()
    
    investment = Investment(
        account_id=request.account_id,
        product_id=request.product_id,
        amount=request.amount,
        created_at=now
    )
    
    transaction = Transaction(
        account_id=request.account_id,
        type='debit',
        amount=-request.amount,
        currency='TWD',
        description='investment purchase',
        created_at=now
    )
    
    session.add(account)
    session.add(investment)
    session.add(transaction)
    session.commit()
    
    return {
        'message': 'purchase successful',
        'new_balance': account.balance
    }
