from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from api.v1.endpoints import auth, accounts, creditcards, investments, loans, utilities, transactions

# HTTPBearer security scheme
security = HTTPBearer(description="Bearer token from /api/v1/auth/login")

api_router = APIRouter()

# Registering routers from each endpoint module (註冊各端點模組的路由器)

# Authentication routes (身份驗證路由)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["身份驗證"]
)

# Account management routes (帳戶管理路由)
api_router.include_router(
    accounts.router, 
    prefix="/accounts", 
    tags=["帳戶管理"],
    dependencies=[Depends(security)]
)

# Credit card management routes (信用卡管理路由)
api_router.include_router(
    creditcards.router, 
    prefix="/creditcards", 
    tags=["信用卡管理"],
    dependencies=[Depends(security)]
)

# Investment management routes (投資理財路由)
api_router.include_router(
    investments.router, 
    prefix="/investments", 
    tags=["投資理財"],
    dependencies=[Depends(security)]
)

# Loan management routes (貸款管理路由)
api_router.include_router(
    loans.router, 
    prefix="/loans", 
    tags=["貸款管理"],
    dependencies=[Depends(security)]
)

# Transaction management routes (交易管理路由)
api_router.include_router(
    transactions.router, 
    prefix="/transactions", 
    tags=["交易管理"],
    dependencies=[Depends(security)]
)

# Utilities management routes (生活繳費路由)
api_router.include_router(
    utilities.router, 
    prefix="/utilities", 
    tags=["生活繳費"],
    dependencies=[Depends(security)]
)
