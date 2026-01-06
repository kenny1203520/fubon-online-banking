from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from models.user import User, SessionModel
from core.database import get_session
from typing import Optional, Annotated
import secrets

SessionDep = Annotated[Session, Depends(get_session)]
security = HTTPBearer(description="Bearer token from /api/v1/auth/login")

def create_user_session(user_id: int, session: Session, hours_valid: int = 24) -> str:
    """
    Create a new user session token. (創建新的使用者session token)  
    Parameters:
    - user_id: The ID of the user (使用者ID)
    - hours_valid: The number of hours the session is valid (session有效時間，單位：小時)
    Returns:
    - The session token (session token)
    """
    token = secrets.token_urlsafe(32) # 生成安全的隨機token
    created = datetime.now(timezone.utc) # 取得當前UTC時間
    expires = created + timedelta(hours=hours_valid) # 計算過期時間
    
    db_session = SessionModel(
        user_id=user_id,
        token=token,
        created_at=created.isoformat(),
        expires_at=expires.isoformat()
    ) # 創建SessionModel實例
    session.add(db_session) # 添加到資料庫session
    session.commit() # 提交更改
    session.refresh(db_session) # 刷新以獲取自動生成的ID
    
    return token

def get_user_by_token(token: str, session: Session) -> Optional[User]:
    """
    Get user by session token. (通過session token獲取使用者)  
    Parameters:
    - token: The session token (session token)
    Returns:
    - User object if valid, else None (如果有效則返回使用者物件，否則返回None)
    """
    if not token:
        return None
    
    statement = select(SessionModel).where(SessionModel.token == token) # 查詢session
    db_session = session.exec(statement).first() # 獲取session資料
    
    if not db_session:
        return None
    
    # 檢查session是否過期
    try:
        expires = datetime.fromisoformat(db_session.expires_at)
    except Exception:
        return None
    
    # 如果session已過期，刪除它
    if datetime.now(timezone.utc) > expires:
        # Session expired, delete it
        session.delete(db_session)
        session.commit()
        return None
    
    # 獲取對應的使用者
    user_statement = select(User).where(User.id == db_session.user_id)
    user = session.exec(user_statement).first()
    
    return user

def verify_token(token: str, session: SessionDep) -> User:
    """
    Verify token and return user. (驗證token並返回使用者)  
    Parameters:
    - token: The session token to verify (要驗證的session token)
    Returns:
    - User object if token is valid (如果token有效則返回使用者物件)
    Raises:
    - HTTPException if token is invalid or expired (如果token無效或過期則引發HTTPException)
    """
    user = get_user_by_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user from HTTPBearer credentials.
    (從HTTPBearer認證信息獲取當前認證使用者)
    
    Expects: Authorization: Bearer <token>
    
    Raises:
    - HTTPException if token is missing or invalid
    """
    token = credentials.credentials
    return verify_token(token, session)
