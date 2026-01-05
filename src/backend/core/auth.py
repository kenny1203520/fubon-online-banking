from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from models.user import User, SessionModel
from core.database import get_session
from typing import Optional, Annotated
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

SessionDep = Annotated[Session, Depends(get_session)]

def create_user_session(user_id: int, session: Session, hours_valid: int = 24) -> str:
    """Create a new user session token."""
    token = secrets.token_urlsafe(32)
    created = datetime.now(timezone.utc)
    expires = created + timedelta(hours=hours_valid)
    
    db_session = SessionModel(
        user_id=user_id,
        token=token,
        created_at=created.isoformat(),
        expires_at=expires.isoformat()
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    
    return token

def get_user_by_token(token: str, session: Session) -> Optional[User]:
    """Get user by session token."""
    if not token:
        return None
    
    statement = select(SessionModel).where(SessionModel.token == token)
    db_session = session.exec(statement).first()
    
    if not db_session:
        return None
    
    # Check if session expired
    try:
        expires = datetime.fromisoformat(db_session.expires_at)
    except Exception:
        return None
    
    if datetime.now(timezone.utc) > expires:
        # Session expired, delete it
        session.delete(db_session)
        session.commit()
        return None
    
    # Get the user
    user_statement = select(User).where(User.id == db_session.user_id)
    user = session.exec(user_statement).first()
    
    return user

def verify_token(token: str, session: SessionDep) -> User:
    """Verify token and return user."""
    user = get_user_by_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user
