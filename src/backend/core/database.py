import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# 在backend資料夾中創建data目錄
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 儲存資料庫於data目錄中
DB_PATH = os.path.join(DATA_DIR, 'database.db')
sqlite_url = f"sqlite:///{DB_PATH}"
connect_args = {"check_same_thread": False}

engine = create_engine(
    sqlite_url,
    connect_args=connect_args,
    echo=False
) # 創建資料庫引擎

def create_db_and_tables():
    """
    Create database tables. (創建資料庫表)  
    This function creates all tables defined in the SQLModel metadata.
    (此函數創建SQLModel元資料中定義的所有表。)
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Get database session. (獲取資料庫session)
    Yields a new SQLModel Session instance.
    (產生一個新的SQLModel session實例。)
    """
    with Session(engine) as session:
        yield session
