from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    """認證錯誤"""
    def __init__(self, detail: str = "認證失敗"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    """授權錯誤"""
    def __init__(self, detail: str = "無權訪問"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class ResourceNotFoundError(HTTPException):
    """資源未找到"""
    def __init__(self, detail: str = "資源未找到"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

class ValidationError(HTTPException):
    """驗證錯誤"""
    def __init__(self, detail: str = "驗證失敗"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )

class ServerError(HTTPException):
    """伺服器錯誤"""
    def __init__(self, detail: str = "伺服器錯誤"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
