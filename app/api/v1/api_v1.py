from fastapi import APIRouter
from app.api.v1.endpoints import (
    cart,
    products,
    payment,
    transactions,
    auth
)

router = APIRouter()

router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(cart.router, prefix="/cart", tags=["cart"])
router.include_router(payment.router, prefix="/payment", tags=["payment"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
