from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import List
from app.models.schemas import TransactionInDB
from app.services import CartService
from app.api.v1.dependencies import get_cart_service, get_user_id
from app.services.exceptions import ServiceException
from app.api.errors import handle_service_error

router = APIRouter()

@router.get("/", response_model=List[TransactionInDB])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    cart_service: CartService = Depends(get_cart_service),
    user_id: int = Depends(get_user_id)
):
    try:
        return await cart_service.get_user_transactions(user_id, skip=skip, limit=limit)
    except ServiceException as exc:
        handle_service_error(exc)

@router.get("/{transaction_id}", response_model=TransactionInDB)
async def get_transaction(
    transaction_id: int,
    cart_service: CartService = Depends(get_cart_service),
    user_id: int = Depends(get_user_id)
):
    try:
        transaction = await cart_service.get_transaction(transaction_id)
        if not transaction or transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction
    except ServiceException as exc:
        handle_service_error(exc)
