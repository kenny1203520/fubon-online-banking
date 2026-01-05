from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI):
    """添加全局錯誤處理器"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """處理驗證錯誤"""
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "驗證失敗",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """處理通用錯誤"""
        logger.error(f"General error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "伺服器錯誤",
                "message": str(exc),
            },
        )
