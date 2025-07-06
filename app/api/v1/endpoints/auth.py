from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import CartService
from app.api.v1.dependencies import get_cart_service, get_session_id
from app.db.session import get_db
from app.models.schemas import Token, UserCreate, UserInDB
from app.db.repositories import user_repo
from app.core.config import settings
from datetime import timedelta
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user
)

router = APIRouter()


@router.post("/signup", response_model=UserInDB)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_repo.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await user_repo.create(db, obj_in=user)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user

@router.post("/merge-cart")
async def merge_guest_cart_with_user(
    cart_service: CartService = Depends(get_cart_service),
    session_id: str = Depends(get_session_id),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    try:
        return await cart_service.merge_carts(session_id, x_user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
