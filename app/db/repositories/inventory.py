from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.db_models import Inventory, Product
from .base import BaseRepository

class InventoryRepository(BaseRepository[Inventory, None, None]):
    def __init__(self):
        super().__init__(Inventory)

    async def get_by_product(
        self, 
        db: AsyncSession, 
        product_id: int,
        load_product: bool = False
    ) -> Optional[Inventory]:
        query = select(Inventory).where(Inventory.product_id == product_id)
        
        if load_product:
            query = query.options(selectinload(Inventory.product))
            
        result = await db.execute(query)
        return result.scalars().first()

    async def check_stock_level(
        self, 
        db: AsyncSession, 
        product_id: int, 
        quantity: int
    ) -> bool:
        inventory = await self.get_by_product(db, product_id)
        if not inventory:
            return False
            
        return inventory.quantity >= quantity

    async def adjust_stock(
        self,
        db: AsyncSession,
        *,
        product_id: int,
        quantity: int
    ) -> Inventory:
        inventory = await self.get_by_product(db, product_id)
        if not inventory:
            raise ValueError("Inventory record not found for product")
            
        new_quantity = inventory.quantity + quantity
        if new_quantity < 0:
            raise ValueError("Insufficient stock available")
            
        inventory.quantity = new_quantity
        await db.commit()
        await db.refresh(inventory)
        return inventory

    async def get_low_stock_items(
        self,
        db: AsyncSession,
        *,
        threshold: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Inventory]:
        query = select(Inventory).options(selectinload(Inventory.product))
        
        if threshold is not None:
            query = query.where(Inventory.quantity <= threshold)
        else:
            query = query.where(
                Inventory.quantity <= Inventory.low_stock_threshold
            )
            
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
