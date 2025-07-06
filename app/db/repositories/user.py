from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.db_models import User
from app.models.schemas import UserCreate, UserInDB
from .base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, None]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        from app.core.security import get_password_hash
        
        # Create username from first_name and last_name if provided
        username = None
        if obj_in.first_name and obj_in.last_name:
            username = f"{obj_in.first_name.lower()}.{obj_in.last_name.lower()}"
        elif obj_in.first_name:
            username = obj_in.first_name.lower()
        else:
            # Use email prefix as username fallback
            username = obj_in.email.split('@')[0]
        
        db_obj = User(
            email=obj_in.email,
            username=username,
            hashed_password=get_password_hash(obj_in.password),
            phone=obj_in.phone_number,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
