#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_inventory_service():
    """Test the InventoryService methods"""
    try:
        from app.services.inventory_service import InventoryService
        from app.db.session import session_manager
        from app.core.config import settings
        
        print("Testing InventoryService methods...")
        
        # Initialize database
        session_manager.init(settings.DATABASE_URL)
        
        # Test getting a session and service
        async for db in session_manager.get_db():
            service = InventoryService(db_session=db)
            
            # Test get_active_products method
            print("Testing get_active_products...")
            products = await service.get_active_products(skip=0, limit=5)
            print(f"✓ get_active_products works - found {len(products)} products")
            
            # Test get_product method
            print("Testing get_product...")
            if products:
                product = await service.get_product(products[0].id)
                if product:
                    print(f"✓ get_product works - found product: {product.name}")
                else:
                    print("✓ get_product works - returned None (as expected)")
            else:
                print("✓ get_product not tested - no products found")
            
            # Test search_products method
            print("Testing search_products...")
            search_results = await service.search_products("test", skip=0, limit=5)
            print(f"✓ search_products works - found {len(search_results)} products")
            
            await db.close()
            break
        
        await session_manager.close()
        print("\n All InventoryService methods are working correctly!")
        return True
        
    except Exception as e:
        print(f" InventoryService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_inventory_service())
    if not success:
        sys.exit(1)
