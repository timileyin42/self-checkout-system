from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.repositories import cart_repo, product_repo, inventory_repo
from app.db.session import get_db
from app.models.schemas import CartItemCreate
from app.services.exceptions import (
    InsufficientStockError,
    AgeVerificationError,
    CartValidationError
)
from app.models.db_models import Cart, CartItem, Product, AgeRestriction

class CartService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_or_create_cart(
        self, 
        user_id: Optional[int] = None, 
        session_id: Optional[str] = None
    ) -> Cart:
        """Get existing active cart or create new one"""
        if user_id:
            cart = await cart_repo.get_by_user(self.db, user_id=user_id)
        elif session_id:
            cart = await cart_repo.get_by_session(self.db, session_id=session_id)
        else:
            raise CartValidationError("Either user_id or session_id must be provided")
        
        if not cart:
            cart_data = {"user_id": user_id} if user_id else {"session_id": session_id}
            cart = await cart_repo.create(self.db, obj_in=cart_data)
        
        return cart

    async def add_item_to_cart(
        self,
        cart_id: int,
        item_data: CartItemCreate,
        skip_stock_check: bool = False
    ) -> CartItem:
        """Add item to cart with validation"""
        # Get product and validate
        product = await product_repo.get(self.db, id=item_data.product_id)
        if not product:
            raise CartValidationError(f"Product {item_data.product_id} not found")
        
        # Check inventory
        if not skip_stock_check:
            inventory = await inventory_repo.get_by_product(self.db, product_id=product.id)
            if not inventory or inventory.quantity < item_data.quantity:
                available = inventory.quantity if inventory else 0
                raise InsufficientStockError(
                    product_id=product.id,
                    available=available,
                    requested=item_data.quantity
                )
        
        # Add item to cart
        try:
            return await cart_repo.add_item_to_cart(
                db=self.db,
                cart_id=cart_id,
                product_id=product.id,
                quantity=item_data.quantity
            )
        except Exception as e:
            raise CartValidationError(f"Failed to add item to cart: {str(e)}")

    async def verify_age_restrictions(self, cart_id: int) -> bool:
        """Check if cart contains age-restricted items"""
        cart = await cart_repo.get_by_id(
            self.db, 
            id=cart_id, 
            load_items=True,
            load_products=True
        )
        
        if not cart:
            raise CartValidationError("Cart not found")
        
        restricted_items = [
            item for item in cart.items
            if item.product.age_restriction != AgeRestriction.NONE
        ]
        
        return len(restricted_items) > 0

    async def calculate_cart_totals(self, cart_id: int) -> Dict[str, Any]:
        """Calculate subtotal, tax, and total for cart"""
        return await cart_repo.calculate_cart_total(self.db, cart_id=cart_id)

    async def clear_cart(self, cart_id: int) -> None:
        """Remove all items from cart"""
        cart = await cart_repo.get_by_id(self.db, id=cart_id, load_items=True)
        if not cart:
            raise CartValidationError("Cart not found")
        
        for item in cart.items:
            await cart_repo.delete_item(self.db, item_id=item.id)
        
        await self.db.commit()

    async def merge_carts(
        self, 
        source_session_id: str, 
        target_user_id: int
    ) -> Cart:
        """Merge guest cart with user cart after login"""
        # Get both carts
        guest_cart = await cart_repo.get_by_session(
            self.db, 
            session_id=source_session_id,
            load_items=True
        )
        user_cart = await cart_repo.get_by_user(
            self.db,
            user_id=target_user_id,
            load_items=True
        )
        
        if not guest_cart:
            return user_cart or await self.get_or_create_cart(user_id=target_user_id)
        
        # If no user cart exists, just assign the guest cart to the user
        if not user_cart:
            guest_cart.user_id = target_user_id
            guest_cart.session_id = None
            await self.db.commit()
            await self.db.refresh(guest_cart)
            return guest_cart
        
        # Merge items from guest cart to user cart
        for guest_item in guest_cart.items:
            existing_item = next(
                (item for item in user_cart.items 
                 if item.product_id == guest_item.product_id),
                None
            )
            
            if existing_item:
                existing_item.quantity += guest_item.quantity
            else:
                await cart_repo.add_item_to_cart(
                    db=self.db,
                    cart_id=user_cart.id,
                    product_id=guest_item.product_id,
                    quantity=guest_item.quantity
                )
        
        # Delete guest cart
        await cart_repo.delete(self.db, id=guest_cart.id)
        await self.db.commit()
        
        return await cart_repo.get_by_user(
            self.db, 
            user_id=target_user_id,
            load_items=True
        )

    # Transaction-related methods
    async def get_user_transactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        """Get user's transaction history"""
        from app.db.repositories import transaction_repo
        return await transaction_repo.get_user_transactions(
            self.db,
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    async def get_transaction(self, transaction_id: int):
        """Get a single transaction with items"""
        from app.db.repositories import transaction_repo
        return await transaction_repo.get_with_items(
            self.db,
            transaction_id=transaction_id
        )
