from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.models.schemas import PaymentCreate
from app.services import PaymentService, CartService
from app.api.v1.dependencies import (
    get_payment_service,
    get_cart_service,
    get_session_id,
    get_user_id
)
from typing import Optional
from app.services.exceptions import ServiceException
from app.api.errors import handle_service_error

router = APIRouter()

@router.post("/checkout")
async def process_checkout(
    payment_data: PaymentCreate,
    payment_service: PaymentService = Depends(get_payment_service),
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    user_id: Optional[int] = Depends(get_user_id)
):
    try:
        cart = await cart_service.get_or_create_cart(user_id=user_id, session_id=session_id)
        cart_totals = await cart_service.calculate_cart_totals(cart.id)
        
        # Create transaction
        transaction = await cart_service.convert_cart_to_transaction(cart.id)
        
        # Process payment
        payment = await payment_service.process_payment(
            transaction_id=transaction.id,
            payment_method=payment_data.method,
            amount=cart_totals["total"],
            payment_details=payment_data.dict()
        )
        
        return {
            "transaction": transaction,
            "payment": payment,
            "receipt_number": payment.receipt_number
        }
    except ServiceException as exc:
        handle_service_error(exc)

@router.post("/refund/{payment_id}")
async def process_refund(
    payment_id: int,
    amount: Optional[float] = None,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        return await payment_service.refund_payment(payment_id, amount)
    except ServiceException as exc:
        handle_service_error(exc)
