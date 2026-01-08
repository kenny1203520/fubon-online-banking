from typing import Optional
from pydantic import BaseModel
import uuid

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    token_id: str
    token: str
    expires_in: int
    message: str

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    admin_code: Optional[str] = None

class UserRegisterResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    message: str

class UserLogoutRequest(BaseModel):
    token_id: str

class UserLogoutResponse(BaseModel):
    message: str

class UserRefreshResponse(BaseModel):
    token: str
    expires_in: int
    message: str

class UserMeResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "user"
    is_admin: bool = False