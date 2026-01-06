from typing import Optional
from pydantic import BaseModel

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

class UserRegisterResponse(BaseModel):
    user_id: int
    username: str
    message: str

class UserLogoutRequest(BaseModel):
    token_id: str

class UserLogoutResponse(BaseModel):
    message: str
