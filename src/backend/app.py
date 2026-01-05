from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from core.config import settings
from contextlib import asynccontextmanager
from api.v1.router import api_router
from core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup/shutdown.
    """
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="富邦網路銀行資訊系統 API",
    description="Fubon Online Banking System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.ALLOWED_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "富邦網路銀行資訊系統 API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=5000)