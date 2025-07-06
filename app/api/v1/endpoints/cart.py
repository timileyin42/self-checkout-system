from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional
from datetime import date
from app.models.schemas import CartInDB, CartItemCreate, CartItemUpdate
from app.services import CartService, AgeVerificationService
from app.api.v1.dependencies import (
    get_cart_service,
    get_age_verification_service,
    get_session_id,
    get_user_id,
    get_birth_date
)
from app.services.exceptions import ServiceException
from app.api.errors import handle_service_error

router = APIRouter()

@router.get("/", response_model=CartInDB)
async def get_cart(
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id)
):
    try:
        return await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    except ServiceException as exc:
        handle_service_error(exc)

@router.post("/items", response_model=CartInDB)
async def add_cart_item(
    item: CartItemCreate,
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id)
):
    try:
        cart = await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
        await cart_service.add_item_to_cart(cart.id, item)
        return await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    except ServiceException as exc:
        handle_service_error(exc)

@router.put("/items/{item_id}", response_model=CartInDB)
async def update_cart_item(
    item_id: int,
    item: CartItemUpdate,
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id)
):
    try:
        cart = await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
        await cart_service.update_cart_item(cart.id, item_id, item)
        return await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    except ServiceException as exc:
        handle_service_error(exc)

@router.delete("/items/{item_id}", response_model=CartInDB)
async def remove_cart_item(
    item_id: int,
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id)
):
    try:
        cart = await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
        await cart_service.remove_item_from_cart(cart.id, item_id)
        return await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
    except ServiceException as exc:
        handle_service_error(exc)

@router.post("/verify-age")
async def verify_cart_age(
    verification_service: AgeVerificationService = Depends(get_age_verification_service),
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id),
    birth_date: Optional[date] = Depends(get_birth_date)
):
    try:
        cart = await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
        if not await cart_service.verify_age_restrictions(cart.id):
            return {"verified": True}
        
        if not birth_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Birth date required in X-Birth-Date header for age verification"
            )
            
        verified = await verification_service.verify_cart_items(cart.id, birth_date)
        return {"verified": verified}
    except ServiceException as exc:
        handle_service_error(exc)

@router.get("/totals")
async def get_cart_totals(
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id)
):
    try:
        cart = await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
        return await cart_service.calculate_cart_totals(cart.id)
    except ServiceException as exc:
        handle_service_error(exc)
