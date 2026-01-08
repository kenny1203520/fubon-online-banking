from sqlmodel import Field, SQLModel
from typing import Optional
import uuid

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    type: str = Field(default="info")  # info | warning | error | success
    title: str
    message: str
    read: bool = Field(default=False, index=True)
    created_at: str
