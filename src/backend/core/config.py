from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """應用配置"""

    # 應用設置
    APP_NAME: str = "Fubon Online Banking"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 伺服器設置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # 資料庫設置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/fubon_banking"
    )

    # JWT 設置
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS 設置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # 信任的主機
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.localhost",
    ]

    # 日誌設置
    LOG_LEVEL: str = "INFO"

    # 郵件設置
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@fubon.com")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
