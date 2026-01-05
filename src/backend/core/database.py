import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Create data directory in backend folder
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Store database in data directory
DB_PATH = os.path.join(DATA_DIR, 'database.db')
sqlite_url = f"sqlite:///{DB_PATH}"
connect_args = {"check_same_thread": False}

engine = create_engine(
    sqlite_url,
    connect_args=connect_args,
    echo=False
)

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session
