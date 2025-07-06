from fastapi import HTTPException, status
from typing import Any, Dict

class AppException(HTTPException):
    """Base application exception"""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, Any] = None,
        error_code: str = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code

class NotFoundException(AppException):
    """Resource not found exception"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="not_found"
        )

class UnauthorizedException(AppException):
    """Authentication/authorization exception"""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="unauthorized"
        )

class ForbiddenException(AppException):
    """Permission denied exception"""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="forbidden"
        )

class BadRequestException(AppException):
    """Invalid request exception"""
    
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="bad_request"
        )
