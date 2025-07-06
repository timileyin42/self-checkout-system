from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional, List
from app.models.schemas import ProductInDB, ProductCreate, ProductUpdate
from app.services import InventoryService
from app.api.v1.dependencies import get_inventory_service
from app.services.exceptions import ServiceException
from app.api.errors import handle_service_error

router = APIRouter()

@router.get("/", response_model=List[ProductInDB])
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    try:
        if search:
            return await inventory_service.search_products(search, skip=skip, limit=limit)
        elif category:
            return await inventory_service.get_products_by_category(category, skip=skip, limit=limit)
        else:
            return await inventory_service.get_active_products(skip=skip, limit=limit)
    except ServiceException as exc:
        handle_service_error(exc)

@router.get("/{product_id}", response_model=ProductInDB)
async def get_product(
    product_id: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    try:
        product = await inventory_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except ServiceException as exc:
        handle_service_error(exc)

@router.get("/{product_id}/inventory")
async def get_product_inventory(
    product_id: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    try:
        inventory = await inventory_service.get_product_inventory(product_id)
        if not inventory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
        return inventory
    except ServiceException as exc:
        handle_service_error(exc)
