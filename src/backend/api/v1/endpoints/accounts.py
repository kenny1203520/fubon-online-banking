from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func
from datetime import datetime, timezone
from typing import Optional

from models.account import Account
from models.transaction import Transaction
from schemas.account import (
    AccountCreate, AccountResponse, AccountList, BalanceRequest, BalanceResponse,
    CashlessRequest, CashlessResponse
)
from schemas.transaction import TransactionList, TransactionResponse
from schemas.credit_card import TransferRequest, TransferResponse
from core.database import get_session

router = APIRouter()

@router.post('/open', status_code=status.HTTP_201_CREATED)
async def open_account(request: AccountCreate, session: Session = Depends(get_session)):
    """Open a new account."""
    account = Account(
        full_name=request.full_name,
        id_number=request.id_number,
        email=request.email,
        balance=request.initial_deposit,
        status='pending',
        created_at=datetime.now(timezone.utc).isoformat()
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return {
        'account_id': account.id,
        'status': 'pending',
        'message': '申請已建立，等待審核'
    }

@router.get('', response_model=AccountList)
async def list_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    """List all accounts with pagination."""
    offset = (page - 1) * per_page
    
    # Get total count
    total = session.exec(func.select(func.count(Account.id))).one()
    
    # Get accounts
    statement = select(Account).order_by(Account.id.desc()).offset(offset).limit(per_page)
    accounts = session.exec(statement).all()
    
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    
    return {
        'items': [AccountResponse.from_orm(acc) for acc in accounts],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    }

@router.post('/balance', response_model=BalanceResponse)
async def get_balance(request: BalanceRequest, session: Session = Depends(get_session)):
    """Get account balance."""
    account = session.get(Account, request.account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='account not found'
        )
    
    return {
        'account_id': account.id,
        'balance': account.balance,
        'cashless_enabled': bool(account.cashless_enabled)
    }

@router.post('/transactions', response_model=TransactionList)
async def get_transactions(
    account_id: int,
    frm: Optional[str] = None,
    to: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get account transactions with optional date range."""
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
async def transfer(request: TransferRequest, session: Session = Depends(get_session)):
    """Transfer money between accounts."""
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
    session: Session = Depends(get_session)
):
    """Enable/disable cashless withdrawal."""
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
