from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import User
from schemas.user import (
    UserLoginRequest, UserLoginResponse, UserRegisterRequest, UserRegisterResponse,
    UserLogoutRequest, UserLogoutResponse
)
from core.database import get_session
from core.auth import create_user_session, get_user_by_token

router = APIRouter()

@router.post('/login', response_model=UserLoginResponse)
async def login(request: UserLoginRequest, session: Session = Depends(get_session)):
    """
    User login endpoint. (使用者登入端點)  
    Validates user credentials and returns a session token upon successful authentication.
    (驗證使用者憑證，並在成功驗證後返回session token。)
    Parameters:
    - username: The username of the user (使用者名稱)
    - password: The password of the user (使用者密碼)
    """
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='missing required fields'
        ) # 處理缺少必填欄位錯誤
    
    statement = select(User).where(User.username == request.username) # 查詢使用者
    user = session.exec(statement).first() # 獲取使用者資料
    
    # 驗證密碼
    if not user or not check_password_hash(user.password_hash, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid credentials'
        ) # 處理無效憑證錯誤
    
    # 確保使用者ID存在
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='user ID is None'
        ) # 處理使用者ID為None錯誤
    
    # 創建使用者session並生成token
    token = create_user_session(user.id, session)
    return {
        'token': token,
        'message': '登入成功',
        'code': 200
    } # 返回登入成功訊息

@router.post('/logout', response_model=UserLogoutResponse)
async def logout(request: UserLogoutRequest, session: Session = Depends(get_session)):
    """
    User logout endpoint. (使用者登出端點)  
    Invalidates the user session associated with the provided token.
    (使該令牌對應的使用者會話失效。)
    Parameters:
    - token: The session token to invalidate (要使無效的session token)
    """
    from models.user import SessionModel
    
    statement = select(SessionModel).where(SessionModel.token == request.token) # 查詢Session
    db_session = session.exec(statement).first() # 獲取Session資料
    
    # 驗證Session是否存在
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token'
        ) # 處理無效token錯誤
    
    # 刪除Session並登出使用者
    session.delete(db_session)
    session.commit()
    
    return {
        'message': '登出成功',
        'code': 200
    } # 返回登出成功訊息

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserRegisterResponse)
async def register(request: UserRegisterRequest, session: Session = Depends(get_session)):
    """
    User registration endpoint. (使用者註冊端點)  
    Creates a new user with the provided username, password, and optional email.
    (提供使用者名稱、密碼和可選電子郵件，建立一個新使用者。)
    Parameters:
    - username: Desired username for the new user (新使用者的使用者名稱)
    """
    # 驗證必填欄位
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='missing required fields'
        ) # 處理缺少必填欄位錯誤
    
    password_hash = generate_password_hash(request.password) # 產生密碼雜湊
    
    try:
        user = User(
            username=request.username,
            password_hash=password_hash,
            email=request.email,
            created_at=datetime.now(timezone.utc).isoformat()
        ) # 建立新使用者
        session.add(user) # 儲存使用者到資料庫
        session.commit() # 提交變更
        session.refresh(user) # 取得自動生成的ID
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='username already exists'
        ) # 處理使用者名稱衝突錯誤
    
    return {
        'user_id': user.id,
        'username': request.username,
        'message': '註冊成功',
        'code': 201
    } # 返回註冊成功訊息
