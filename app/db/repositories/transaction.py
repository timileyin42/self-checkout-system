from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload
from app.models.db_models import Transaction, TransactionItem, TransactionStatus
from app.models.schemas import TransactionCreate
from .base import BaseRepository

class TransactionRepository(BaseRepository[Transaction, TransactionCreate, None]):
    def __init__(self):
        super().__init__(Transaction)

    async def get_with_items(
        self, 
        db: AsyncSession, 
        transaction_id: int
    ) -> Optional[Transaction]:
        result = await db.execute(
            select(Transaction)
            .options(
                selectinload(Transaction.items)
                .selectinload(TransactionItem.product),
                selectinload(Transaction.payments)
            )
            .where(Transaction.id == transaction_id)
        )
        return result.scalars().first()

    async def get_user_transactions(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_from_cart(
        self,
        db: AsyncSession,
        *,
        cart_id: int,
        user_id: int,
        payment_method: str,
        total_amount: float
    ) -> Transaction:
        # Get cart with items
        cart = await db.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.id == cart_id)
        )
        cart = cart.scalars().first()
        
        if not cart:
            raise ValueError("Cart not found")
            
        # Calculate totals (would normally come from service layer)
        subtotal = sum(item.quantity * item.price_at_addition for item in cart.items)
        tax = sum(
            item.quantity * item.price_at_addition * item.product.tax_rate 
            for item in cart.items
        )
        
        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            cart_id=cart_id,
            status=TransactionStatus.COMPLETED,
            subtotal=subtotal,
            tax_amount=tax,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING,
            completed_at=datetime.utcnow()
        )
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        
        # Create transaction items
        for cart_item in cart.items:
            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.price_at_addition,
                tax_rate=cart_item.product.tax_rate,
                was_age_verified=cart_item.is_age_verified
            )
            db.add(transaction_item)
        
        # Mark cart as inactive
        cart.is_active = False
        await db.commit()
        
        return transaction
