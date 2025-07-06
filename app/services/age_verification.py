from datetime import datetime, date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.repositories import cart_repo
from app.db.session import get_db
from app.models.db_models import Cart, AgeRestriction
from app.services.exceptions import AgeVerificationError

class AgeVerificationService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def verify_cart_items(
        self,
        cart_id: int,
        birth_date: Optional[date] = None
    ) -> bool:
        """Verify age for all restricted items in cart"""
        cart = await cart_repo.get_by_id(
            self.db,
            id=cart_id,
            load_items=True,
            load_products=True
        )
        
        if not cart:
            raise AgeVerificationError("Cart not found")
        
        restricted_items = [
            item for item in cart.items
            if item.product.age_restriction != AgeRestriction.NONE
        ]
        
        if not restricted_items:
            return True
        
        if not birth_date:
            raise AgeVerificationError("Birth date required for age verification")
        
        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        
        for item in restricted_items:
            required_age = self._get_required_age(item.product.age_restriction)
            if age < required_age:
                raise AgeVerificationError(
                    f"Item {item.product.name} requires age {required_age}+"
                )
        
        # Mark items as verified
        for item in restricted_items:
            item.is_age_verified = True
        await self.db.commit()
        
        return True

    def _get_required_age(self, restriction: AgeRestriction) -> int:
        """Map restriction enum to minimum age"""
        if restriction == AgeRestriction.AGE_18:
            return 18
        elif restriction == AgeRestriction.AGE_21:
            return 21
        return 0  # Shouldn't happen for verified items
