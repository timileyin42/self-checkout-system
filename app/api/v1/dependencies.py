from fastapi import Depends, Header, HTTPException, status
from typing import Optional, AsyncGenerator
from datetime import date
from app.db.session import get_db as db_session_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import (
    CartService,
    PaymentService,
    InventoryService,
    ReceiptService,
    AgeVerificationService
)
from app.services.exceptions import ServiceException
from app.api.errors import handle_service_error

async def get_cart_service():
    return CartService()

async def get_payment_service():
    return PaymentService()

async def get_inventory_service():
    return InventoryService()

async def get_receipt_service():
    return ReceiptService()

async def get_age_verification_service():
    return AgeVerificationService()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_session_get_db():
        yield session

async def get_session_id(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
) -> str:
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID header is required"
        )
    return x_session_id

async def get_user_id(
    x_user_id: Optional[int] = Header(None, alias="X-User-ID")
) -> Optional[int]:
    return x_user_id

async def get_birth_date(
    x_birth_date: Optional[str] = Header(None, alias="X-Birth-Date")
) -> Optional[date]:
    if x_birth_date:
        try:
            return date.fromisoformat(x_birth_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid birth date format. Use YYYY-MM-DD"
            )
    return None
