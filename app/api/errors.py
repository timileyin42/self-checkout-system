from fastapi import HTTPException, status
from app.services.exceptions import (
    ServiceException,
    InsufficientStockError,
    AgeVerificationError,
    PaymentProcessingError,
    CartValidationError
)

def handle_service_error(exc: ServiceException):
    """Convert service exceptions to HTTP exceptions"""
    if isinstance(exc, InsufficientStockError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Insufficient stock",
                "product_id": exc.product_id,
                "available": exc.available,
                "requested": exc.requested
            }
        )
    elif isinstance(exc, AgeVerificationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        )
    elif isinstance(exc, PaymentProcessingError):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exc)
        )
    elif isinstance(exc, CartValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
