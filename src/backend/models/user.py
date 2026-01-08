from sqlmodel import Field, SQLModel
from typing import Optional
import uuid

class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    email: Optional[str] = Field(default=None, index=True)
    is_admin: bool = Field(default=False, index=True)
    role: str = Field(default="user", index=True)
    created_at: str

class SessionModel(SQLModel, table=True):
    """
    雙 Token 機制session模型
    (Dual Token Mechanism Session Model)
    """
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    token_id: str = Field(index=True, default_factory=lambda: str(uuid.uuid4())) # 唯一 token ID
    access_token: str = Field(index=True)  # 短期 token
    refresh_token: str = Field(index=True) # 長期 token
    access_token_expires_at: str  # Access token 過期時間
    refresh_token_expires_at: str # Refresh token 過期時間
    created_at: str
    revoked: bool = Field(default=False) # 標記該 token 是否已被撤銷
