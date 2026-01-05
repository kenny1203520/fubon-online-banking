from fastapi import APIRouter
from .endpoints import auth, accounts, creditcards, investments, loans

api_router = APIRouter()

# Registering routers from each endpoint module

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Account management routes
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])

# Credit card management routes
api_router.include_router(creditcards.router, prefix="/creditcards", tags=["creditcards"])

# Investment management routes
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])

# Loan management routes
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])