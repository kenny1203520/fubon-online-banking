from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True, # 保留認證信息
        "syntaxHighlight": {
            "activate": True,
            "theme": "monokai"
        }
    }
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.ALLOWED_ORIGINS,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/", status_code=status.HTTP_302_FOUND)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Fix for Windows asyncio event loop issue
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    uvicorn.run(
        app,
        port=5000,
        loop="asyncio",
        log_level="info"
    )