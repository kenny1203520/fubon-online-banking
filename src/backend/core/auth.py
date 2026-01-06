from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from models.user import User, SessionModel
from core.database import get_session
from typing import Optional, Annotated, Tuple, Dict, Any
import secrets
import bcrypt
import uuid

SessionDep = Annotated[Session, Depends(get_session)]
security = HTTPBearer(description="Bearer token from /api/v1/auth/login")

# Token 配置
ACCESS_TOKEN_EXPIRE_MINUTES = 10 # 訪問token有效期：10 分鐘
REFRESH_TOKEN_EXPIRE_DAYS = 7    # 刷新token有效期：7 天

# ============== 密碼加密和驗證 ==============
def hash_password(password: str) -> str:
    """
    使用 bcrypt 對密碼進行雜湊加密
    (Hash password using bcrypt)
    
    Parameters:
    - password: 明文密碼 (plain password)
    Returns:
    - 加密後的密碼雜湊 (hashed password)
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼是否與雜湊匹配
    (Verify if plain password matches the hash)
    
    Parameters:
    - plain_password: 明文密碼 (plain password)
    - hashed_password: 存儲的雜湊密碼 (stored hash)
    Returns:
    - 驗證結果 (bool)
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ============== Token 生成和驗證 ==============
def create_token(expires_delta: Optional[timedelta] = None) -> str:
    """
    生成一個安全的隨機 token
    (Generate a secure random token)
    
    Parameters:
    - expires_delta: Token 過期時間 (token expiration time)
    Returns:
    - 生成的 token 字串 (generated token string)
    """
    return secrets.token_urlsafe(32)

def create_user_tokens(user_id: int, session: Session) -> Dict[str, Any]:
    """
    為用戶創建訪問token和刷新token（雙 Token 機制）
    (Create access and refresh tokens for user - Dual Token Mechanism)
    
    Parameters:
    - user_id: 用戶 ID (user ID)
    - session: 資料庫 session (database session)
    
    Returns:
    - 包含 tokens 和過期時間的字典：
    {
        "token_id": "唯一 token ID",
        "access_token": "訪問token",
        "refresh_token": "刷新token",
        "access_token_expires_in": 600, # 訪問token過期時間 (秒)
        "refresh_token_expires_in": 604800 # 刷新token過期時間 (秒)
    }
    """
    now = datetime.now(timezone.utc) # 當前時間
    token_id = str(uuid.uuid4()) # 唯一 token ID
    
    # 生成 tokens
    access_token = create_token()
    refresh_token = create_token()
    
    # 計算過期時間
    access_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # 保存到資料庫
    db_session = SessionModel(
        user_id=user_id,
        token_id=token_id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires_at=access_expires.isoformat(),
        refresh_token_expires_at=refresh_expires.isoformat(),
        created_at=now.isoformat(),
        revoked=False
    ) # 建立session模型
    
    session.add(db_session) # 儲存session到資料庫
    session.commit() # 提交變更
    session.refresh(db_session) # 取得自動生成的ID
    
    return {
        "token_id": token_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60, # 秒
        "refresh_token_expires_in": REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600 # 秒
    } # 返回生成的 tokens 和過期時間

def verify_access_token(token: str, session: Session) -> Tuple[Optional[User], Optional[str]]:
    """
    驗證訪問token並返回用戶和 token_id
    (Verify access token and return user and token_id)
    
    Parameters:
    - token: 訪問token (access token)
    - session: 資料庫 session (database session)
    
    Returns:
    - (user, token_id) 元組，如果token無效則返回 (None, None)
    """
    if not token:
        return None, None
    
    # 查找session
    statement = select(SessionModel).where(SessionModel.access_token == token)
    db_session = session.exec(statement).first()
    
    # 檢查session是否存在且未被撤銷
    if not db_session or db_session.revoked:
        return None, None
    
    # 驗證訪問token是否過期
    try:
        expires = datetime.fromisoformat(db_session.access_token_expires_at)
    except Exception:
        return None, None
    
    if datetime.now(timezone.utc) > expires:
        return None, None
    
    # 獲取用戶
    user_statement = select(User).where(User.id == db_session.user_id)
    user = session.exec(user_statement).first()
    
    return user, db_session.token_id

def verify_refresh_token(token: str, session: Session) -> Optional[str]:
    """
    驗證刷新token並返回 token_id
    (Verify refresh token and return token_id for token rotation)
    
    Parameters:
    - token: 刷新token (refresh token)
    - session: 資料庫 session (database session)
    
    Returns:
    - token_id 如果有效，否則 None
    """
    if not token:
        return None
    
    statement = select(SessionModel).where(SessionModel.refresh_token == token)
    db_session = session.exec(statement).first()
    
    if not db_session or db_session.revoked:
        return None
    
    # 驗證刷新token是否過期
    try:
        expires = datetime.fromisoformat(db_session.refresh_token_expires_at)
    except Exception:
        return None
    
    if datetime.now(timezone.utc) > expires:
        return None
    
    return db_session.token_id

def rotate_tokens(token_id: str, session: Session) -> Optional[Dict[str, Any]]:
    """
    使用刷新token生成新的訪問token
    (Rotate tokens using refresh token to get new access token)
    
    Parameters:
    - token_id: 舊的 token ID (old token ID)
    - session: 資料庫 session (database session)
    
    Returns:
    - 新的 token 資訊，或 None 如果失敗
    """
    # 找到session
    statement = select(SessionModel).where(SessionModel.token_id == token_id)
    db_session = session.exec(statement).first()
    
    if not db_session or db_session.revoked:
        return None
    
    # 生成新的訪問token
    now = datetime.now(timezone.utc)
    new_access_token = create_token()
    new_access_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 更新session
    db_session.access_token = new_access_token
    db_session.access_token_expires_at = new_access_expires.isoformat()
    
    session.add(db_session) # 儲存更新到資料庫
    session.commit() # 提交變更
    session.refresh(db_session) # 重新整理
    
    return {
        "token_id": db_session.token_id,
        "access_token": new_access_token,
        "access_token_expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    } # 返回新的訪問token資訊

def revoke_token(token_id: str, session: Session) -> bool:
    """
    撤銷指定的token（登出時調用）
    (Revoke a token (called during logout))
    
    Parameters:
    - token_id: 要撤銷的 token ID (token ID to revoke)
    - session: 資料庫 session (database session)
    
    Returns:
    - 撤銷是否成功 (bool)
    """
    # 找到session
    statement = select(SessionModel).where(SessionModel.token_id == token_id)
    db_session = session.exec(statement).first()
    
    if not db_session:
        return False
    
    db_session.revoked = True # 標記為已撤銷
    session.add(db_session) # 儲存更新到資料庫
    session.commit() # 提交變更
    
    return True

# ============== FastAPI 依賴函數 ==============
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    從 Authorization header 獲取當前認證用戶（使用訪問token）
    (Get current authenticated user from Authorization header using access token)
    
    Expects: Authorization: Bearer <access_token>
    
    Raises:
    - HTTPException 如果token無效或過期 (if token is invalid or expired)
    """
    # 提取token
    token = credentials.credentials
    user, token_id = verify_access_token(token, session)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    
    return user
