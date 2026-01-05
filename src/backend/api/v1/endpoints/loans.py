from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from datetime import datetime, timezone

from models.loan import Loan
from schemas.loan import LoanApplyRequest, LoanApplyResponse
from core.database import get_session

router = APIRouter()

@router.post('/apply', status_code=status.HTTP_201_CREATED, response_model=LoanApplyResponse)
async def apply_loan(request: LoanApplyRequest, session: Session = Depends(get_session)):
    """Apply for a loan."""
    now = datetime.now(timezone.utc).isoformat()
    
    loan = Loan(
        user_id=request.user_id,
        amount=request.amount,
        status='applied',
        created_at=now
    )
    
    session.add(loan)
    session.commit()
    session.refresh(loan)
    
    return {
        'loan_id': loan.id,
        'status': 'applied',
        'message': '貸款申請已提交'
    }
