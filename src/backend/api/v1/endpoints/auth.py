from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
import sqlite3
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
    """User login endpoint."""
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='missing required fields'
        )
    
    statement = select(User).where(User.username == request.username)
    user = session.exec(statement).first()
    
    if not user or not check_password_hash(user.password_hash, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid credentials'
        )
    
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='user ID is None'
        )
    
    token = create_user_session(user.id, session)
    return {
        'token': token,
        'message': '登入成功',
        'code': 200
    }


@router.post('/logout', response_model=UserLogoutResponse)
async def logout(request: UserLogoutRequest, session: Session = Depends(get_session)):
    """User logout endpoint."""
    from models.user import SessionModel
    
    statement = select(SessionModel).where(SessionModel.token == request.token)
    db_session = session.exec(statement).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token'
        )
    
    session.delete(db_session)
    session.commit()
    
    return {
        'message': '登出成功',
        'code': 200
    }


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserRegisterResponse)
async def register(request: UserRegisterRequest, session: Session = Depends(get_session)):
    """User registration endpoint."""
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='missing required fields'
        )
    
    password_hash = generate_password_hash(request.password)
    
    try:
        user = User(
            username=request.username,
            password_hash=password_hash,
            email=request.email,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='username already exists'
        )
    
    return {
        'user_id': user.id,
        'username': request.username,
        'message': '註冊成功',
        'code': 201
    }