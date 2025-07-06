from typing import Optional
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.db_models import Product, ProductStatus
from app.models.schemas import ProductCreate, ProductUpdate
from .base import BaseRepository

class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(Product)

    async def get_by_barcode(self, db: AsyncSession, barcode: str) -> Optional[Product]:
        result = await db.execute(
            select(Product).where(Product.barcode == barcode)
        )
        return result.scalars().first()

    async def get_active_products(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Product]:
        result = await db.execute(
            select(Product)
            .where(Product.status == ProductStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search_products(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Product]:
        search = f"%{search_term}%"
        result = await db.execute(
            select(Product)
            .where(
                or_(
                    Product.name.ilike(search),
                    Product.barcode.ilike(search),
                    Product.description.ilike(search)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_products_by_category(
        self,
        db: AsyncSession,
        *,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Product]:
        result = await db.execute(
            select(Product)
            .where(Product.category == category)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
