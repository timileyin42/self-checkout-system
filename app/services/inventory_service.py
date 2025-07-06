from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories import inventory_repo, product_repo
from app.models.db_models import Inventory, Product
from app.services.exceptions import InsufficientStockError

class InventoryService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_product_inventory(self, product_id: int) -> Optional[Inventory]:
        """Get inventory record for product"""
        return await inventory_repo.get_by_product(
            self.db, 
            product_id=product_id,
            load_product=True
        )

    async def check_stock_level(
        self, 
        product_id: int, 
        quantity: int
    ) -> bool:
        """Check if sufficient stock exists"""
        inventory = await inventory_repo.get_by_product(self.db, product_id=product_id)
        if not inventory:
            return False
        return inventory.quantity >= quantity

    async def adjust_inventory(
        self,
        product_id: int,
        quantity: int
    ) -> Inventory:
        """Adjust inventory levels (positive or negative)"""
        if quantity == 0:
            raise ValueError("Quantity must be positive or negative")
        
        inventory = await inventory_repo.get_by_product(self.db, product_id=product_id)
        if not inventory:
            raise ValueError("Inventory record not found")
        
        new_quantity = inventory.quantity + quantity
        if new_quantity < 0:
            raise InsufficientStockError(
                product_id=product_id,
                available=inventory.quantity,
                requested=abs(quantity)
            )
        
        return await inventory_repo.adjust_stock(
            self.db,
            product_id=product_id,
            quantity=quantity
        )

    async def get_low_stock_items(
        self,
        threshold: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inventory]:
        """Get items below stock threshold"""
        return await inventory_repo.get_low_stock_items(
            self.db,
            threshold=threshold,
            skip=skip,
            limit=limit
        )

    async def bulk_update_inventory(
        self,
        updates: List[Dict[str, int]]  # List of {product_id: int, adjustment: int}
    ) -> List[Inventory]:
        """Process multiple inventory adjustments in a transaction"""
        results = []
        for update in updates:
            try:
                adjusted = await self.adjust_inventory(
                    product_id=update["product_id"],
                    quantity=update["adjustment"]
                )
                results.append(adjusted)
            except Exception as e:
                await self.db.rollback()
                raise
                
        await self.db.commit()
        return results

    async def get_active_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get all active products"""
        return await product_repo.get_active_products(
            self.db,
            skip=skip,
            limit=limit
        )

    async def search_products(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Search products by name or description"""
        return await product_repo.search_products(
            self.db,
            search_term=search_term,
            skip=skip,
            limit=limit
        )

    async def get_products_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by category"""
        return await product_repo.get_products_by_category(
            self.db,
            category=category,
            skip=skip,
            limit=limit
        )

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get a single product by ID"""
        return await product_repo.get_by_id(self.db, product_id)

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get a single product by ID (alias for get_product_by_id)"""
        return await self.get_product_by_id(product_id)

    async def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get a product by its barcode"""
        return await product_repo.get_by_barcode(self.db, barcode)
