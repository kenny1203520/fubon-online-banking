from fastapi import APIRouter
from .endpoints import auth, accounts, creditcards, investments, loans

api_router = APIRouter()

# Registering routers from each endpoint module (註冊各端點模組的路由器)

# Authentication routes (身份驗證路由)
api_router.include_router(auth.router, prefix="/auth", tags=["身份驗證"])

# Account management routes (帳戶管理路由)
api_router.include_router(accounts.router, prefix="/accounts", tags=["帳戶管理"])

# Credit card management routes (信用卡管理路由)
api_router.include_router(creditcards.router, prefix="/creditcards", tags=["信用卡管理"])

# Investment management routes (投資理財路由)
api_router.include_router(investments.router, prefix="/investments", tags=["投資理財"])

# Loan management routes (貸款管理路由)
api_router.include_router(loans.router, prefix="/loans", tags=["貸款管理"])