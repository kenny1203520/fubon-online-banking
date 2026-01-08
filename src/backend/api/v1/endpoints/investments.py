from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from typing import Optional

from models.investment import Investment
from models.account import Account
from models.transaction import Transaction
from models.user import User
from models.investment_product import InvestmentProduct
from schemas.investment import (
    InvestmentList, InvestmentResponse, InvestmentPurchaseRequest, InvestmentPurchaseResponse
)
from schemas.investment_product import InvestmentProductList, InvestmentProductResponse
from data.investment_products import PRODUCTS
from core.database import get_session
from core.auth import get_current_user

router = APIRouter()

@router.post('/query', response_model=InvestmentList)
async def query_investments(
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
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


@router.get('/products', response_model=InvestmentProductList)
async def list_products():
    """
    List available investment products (列出可投資的產品)
    """
    return {'items': [InvestmentProductResponse(**p) for p in PRODUCTS]}


@router.get('/funds', response_model=InvestmentProductList)
async def list_funds(risk_level: Optional[str] = None):
    """
    List funds (簡易版，使用 investment products 作為基金資料來源)
    """
    items = [p for p in PRODUCTS]
    if risk_level:
        items = [p for p in items if p.get('risk_level') == risk_level]
    return {'items': [InvestmentProductResponse(**p) for p in items]}


@router.get('/funds/{fund_id}', response_model=InvestmentProductResponse)
async def get_fund(fund_id: int):
    p = next((x for x in PRODUCTS if x['id'] == fund_id), None)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='fund not found')
    return InvestmentProductResponse(**p)


@router.post('/funds/purchase', response_model=InvestmentPurchaseResponse)
async def purchase_fund(
    request: InvestmentPurchaseRequest,
    session: Session = Depends(get_session)
):
    """
    Purchase a fund (uses same flow as general purchase)
    """
    account = session.get(Account, request.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='account not found')

    product = next((p for p in PRODUCTS if p['id'] == int(request.product_id)), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')

    if request.amount < float(product.get('min_amount', 0)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'minimum investment amount is {product.get("min_amount")}')

    if account.balance < request.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='insufficient funds')

    account.balance -= request.amount
    now = datetime.now(timezone.utc).isoformat()

    investment = Investment(
        account_id=request.account_id,
        product_id=str(request.product_id),
        amount=request.amount,
        created_at=now
    )

    transaction = Transaction(
        account_id=request.account_id,
        type='debit',
        amount=-request.amount,
        currency='TWD',
        description='fund purchase',
        created_at=now
    )

    session.add(account)
    session.add(investment)
    session.add(transaction)
    session.commit()

    return {'message': 'fund purchase successful', 'new_balance': account.balance}

@router.post('/purchase', response_model=InvestmentPurchaseResponse)
async def purchase_investment(
    request: InvestmentPurchaseRequest,
    current_user: User = Depends(get_current_user),
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
    
    # validate product exists and min amount
    product = next((p for p in PRODUCTS if p['id'] == int(request.product_id)), None)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='product not found'
        )

    if request.amount < float(product.get('min_amount', 0)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'minimum investment amount is {product.get("min_amount")}'
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
        product_id=str(request.product_id),
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
