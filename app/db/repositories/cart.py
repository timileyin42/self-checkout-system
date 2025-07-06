from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models.db_models import Cart, CartItem, Product
from app.models.schemas import CartItemCreate
from .base import BaseRepository

class CartRepository(BaseRepository[Cart, None, None]):
    def __init__(self):
        super().__init__(Cart)

    async def get_by_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        load_items: bool = True
    ) -> Optional[Cart]:
        query = select(Cart).where(Cart.user_id == user_id, Cart.is_active == True)
        
        if load_items:
            query = query.options(selectinload(Cart.items).selectinload(CartItem.product))
            
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_session(
        self, 
        db: AsyncSession, 
        session_id: str, 
        load_items: bool = True
    ) -> Optional[Cart]:
        query = select(Cart).where(Cart.session_id == session_id, Cart.is_active == True)
        
        if load_items:
            query = query.options(selectinload(Cart.items).selectinload(CartItem.product))
            
        result = await db.execute(query)
        return result.scalars().first()

    async def add_item_to_cart(
        self,
        db: AsyncSession,
        *,
        cart_id: int,
        product_id: int,
        quantity: int
    ) -> CartItem:
        # Check if item already exists in cart
        existing_item = await db.execute(
            select(CartItem)
            .where(and_(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id
            ))
        )
        existing_item = existing_item.scalars().first()
        
        if existing_item:
            existing_item.quantity += quantity
            await db.commit()
            await db.refresh(existing_item)
            return existing_item
        
        # Get product price
        product = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product.scalars().first()
        
        if not product:
            raise ValueError("Product not found")
        
        # Create new cart item
        new_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            price_at_addition=product.current_price
        )
        
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        return new_item

    async def calculate_cart_total(self, db: AsyncSession, cart_id: int) -> dict:
        result = await db.execute(
            select(
                func.sum(CartItem.quantity * CartItem.price_at_addition).label("subtotal"),
                func.sum(
                    CartItem.quantity * CartItem.price_at_addition * 
                    Product.tax_rate
                ).label("tax"),
                func.count(CartItem.id).label("item_count")
            )
            .join(Product, CartItem.product_id == Product.id)
            .where(CartItem.cart_id == cart_id)
        )
        
        totals = result.first()
        return {
            "subtotal": totals.subtotal or 0,
            "tax": totals.tax or 0,
            "total": (totals.subtotal or 0) + (totals.tax or 0),
            "item_count": totals.item_count or 0
        }
