from typing import Optional
from pydantic import BaseModel

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    token: str
    message: str
    code: int

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserRegisterResponse(BaseModel):
    user_id: int
    username: str
    message: str
    code: int

class UserLogoutRequest(BaseModel):
    token: str

class UserLogoutResponse(BaseModel):
    message: str
    code: int
