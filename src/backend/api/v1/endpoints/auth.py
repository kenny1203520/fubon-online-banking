from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from sqlmodel import Session, select
from datetime import datetime, timezone
from models.user import User
from schemas.user import (
    UserLoginRequest, UserLoginResponse, UserRegisterRequest, UserRegisterResponse,
    UserLogoutRequest, UserLogoutResponse
)
from core.database import get_session
from core.auth import (
    create_user_tokens, verify_refresh_token, rotate_tokens, 
    revoke_token, hash_password, verify_password
)

router = APIRouter()

@router.post('/login', name="使用者登入", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def login(request: UserLoginRequest, response: Response, session: Session = Depends(get_session)):
    """
    User login endpoint with dual token mechanism.
    (使用者登入端點 - 採用雙 Token 機制)
    
    Returns:
    - access_token: 短期有效（10分鐘）的訪問token (Short-lived access token)
    - Refresh token: 在 HttpOnly Cookie 中返回 7 天有效期的刷新token (HttpOnly cookie with 7-day refresh token)
    
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
    
    # 驗證密碼 (使用 bcrypt)
    if not user or not verify_password(request.password, user.password_hash):
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
    
    # 生成雙 Token
    tokens = create_user_tokens(user.id, session)
    
    # 設置刷新令牌為 HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=tokens["refresh_token_expires_in"], # 7 days in seconds
        httponly=True, # 防止 JavaScript 訪問
        secure=True, # 僅通過 HTTPS 發送
        samesite="strict" # 防止 CSRF 攻擊
    )
    
    return {
        'token': tokens["access_token"], # 返回訪問token
        'token_id': tokens["token_id"], # 返回 token ID 用於追蹤
        'expires_in': tokens["access_token_expires_in"], # 10 分鐘
        'message': '登入成功',
        'code': 200
    } # 返回登入成功訊息

@router.post('/logout', name="使用者登出", status_code=status.HTTP_200_OK, response_model=UserLogoutResponse)
async def logout(request: UserLogoutRequest, response: Response, session: Session = Depends(get_session)):
    """
    User logout endpoint. (使用者登出端點)
    
    撤銷當前的訪問token和刷新token。
    (Revokes the current access token and refresh token)
    
    Parameters:
    - token_id: 要撤銷的 token ID (token ID to revoke)
    """
    # 撤銷token
    success = revoke_token(request.token_id, session)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token'
        )
    
    # 清除刷新token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return {
        'message': '登出成功',
        'code': 200
    } # 返回登出成功訊息

@router.post('/register', name="使用者註冊", status_code=status.HTTP_201_CREATED, response_model=UserRegisterResponse)
async def register(request: UserRegisterRequest, session: Session = Depends(get_session)):
    """
    User registration endpoint. (使用者註冊端點)
    
    使用 bcrypt 加密密碼，建立新用戶。
    (Creates a new user with bcrypt-encrypted password)
    
    Parameters:
    - username: Desired username for the new user (新使用者的使用者名稱)
    - password: Password for the new user (密碼)
    - email: Optional email address (選用的電子郵件)
    """
    # 驗證必填欄位
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='missing required fields'
        ) # 處理缺少必填欄位錯誤
    
    # 使用 bcrypt 加密密碼
    password_hash = hash_password(request.password)
    
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

@router.post('/refresh', name="刷新訪問token", status_code=status.HTTP_200_OK)
async def refresh(request: Request, session: Session = Depends(get_session)):
    """
    Token refresh endpoint. (刷新token端點)
    
    使用刷新token獲取新的訪問token。
    (Use refresh token from HttpOnly cookie to get new access token)
    
    Parameters:
    - Cookie 中的 refresh_token (refresh token in HttpOnly cookie)
    """
    # 從 cookie 中獲取刷新token
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='refresh token missing'
        )
    
    # 驗證刷新token
    token_id = verify_refresh_token(refresh_token, session)
    
    if not token_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid or expired refresh token'
        )
    
    # 旋轉token - 生成新的訪問token
    new_tokens = rotate_tokens(token_id, session)
    
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='token rotation failed'
        )
    
    return {
        'access_token': new_tokens['access_token'],
        'expires_in': new_tokens['access_token_expires_in'], # 秒數
        'message': 'token刷新成功',
        'code': 200
    } # 返回新的訪問token訊息
