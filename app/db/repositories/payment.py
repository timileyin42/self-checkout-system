from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.db_models import Payment, Transaction
from app.models.schemas import PaymentCreate
from .base import BaseRepository

class PaymentRepository(BaseRepository[Payment, PaymentCreate, None]):
    def __init__(self):
        super().__init__(Payment)

    async def get_by_reference(
        self, 
        db: AsyncSession, 
        reference: str,
        load_transaction: bool = False
    ) -> Optional[Payment]:
        query = select(Payment).where(Payment.processor_reference == reference)
        
        if load_transaction:
            query = query.options(selectinload(Payment.transaction))
            
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_transaction(
        self,
        db: AsyncSession,
        transaction_id: int,
        load_transaction: bool = False
    ) -> List[Payment]:
        query = select(Payment).where(Payment.transaction_id == transaction_id)
        
        if load_transaction:
            query = query.options(selectinload(Payment.transaction))
            
        result = await db.execute(query)
        return result.scalars().all()

    async def get_successful_payments(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        result = await db.execute(
            select(Payment)
            .where(Payment.status == "completed")
            .order_by(Payment.processed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_failed_payments(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        result = await db.execute(
            select(Payment)
            .where(Payment.status == "failed")
            .order_by(Payment.processed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_payments_by_method(
        self,
        db: AsyncSession,
        method: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        result = await db.execute(
            select(Payment)
            .where(Payment.method == method)
            .order_by(Payment.processed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
