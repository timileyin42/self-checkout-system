from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, condecimal, conint, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserInDB(UserBase):
    id: int
    is_active: bool
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ProductBase(BaseModel):
    barcode: str = Field(..., max_length=50)
    sku: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: str  # Will be replaced with ProductCategory enum
    current_price: condecimal(gt=0, decimal_places=2)
    cost_price: Optional[condecimal(ge=0, decimal_places=2)] = None
    tax_rate: condecimal(ge=0, le=1, decimal_places=4) = 0.0
    requires_serial_number: bool = False
    is_weighted: bool = False

    @validator('category')
    def validate_category(cls, v):
        if v not in [e.value for e in ProductCategory]:
            raise ValueError("Invalid product category")
        return v


class ProductCreate(ProductBase):
    age_restriction: Optional[str] = "none"  # Will be replaced with AgeRestriction enum
    low_stock_threshold: Optional[conint(ge=0)] = 10
    reorder_threshold: Optional[conint(ge=0)] = 5

    @validator('age_restriction')
    def validate_age_restriction(cls, v):
        if v not in [e.value for e in AgeRestriction]:
            raise ValueError("Invalid age restriction")
        return v


class ProductUpdate(BaseModel):
    current_price: Optional[condecimal(gt=0, decimal_places=2)] = None
    status: Optional[str] = None  # Will be replaced with ProductStatus enum
    description: Optional[str] = Field(None, max_length=500)

    @validator('status')
    def validate_status(cls, v):
        if v and v not in [e.value for e in ProductStatus]:
            raise ValueError("Invalid product status")
        return v


class ProductInDB(ProductBase):
    id: int
    status: str  # Will be replaced with ProductStatus enum
    age_restriction: str  # Will be replaced with AgeRestriction enum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryLevel(BaseModel):
    quantity: conint(ge=0)
    low_stock_threshold: conint(ge=0)
    reorder_threshold: conint(ge=0)
    is_active: bool


class CartItemCreate(BaseModel):
    product_id: int
    quantity: conint(gt=0) = 1


class CartItemUpdate(BaseModel):
    quantity: conint(gt=0)


class CartItemInDB(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_addition: condecimal(ge=0, decimal_places=2)
    added_at: datetime

    class Config:
        from_attributes = True


class CartInDB(BaseModel):
    id: int
    user_id: Optional[int]
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[CartItemInDB] = []

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    method: str  # Will be replaced with PaymentMethod enum
    amount: condecimal(gt=0, decimal_places=2)
    processor_reference: Optional[str] = None
    last_four_digits: Optional[str] = Field(default=None, pattern=r'^\d{4}$')

    @validator('method')
    def validate_method(cls, v):
        if v not in [e.value for e in PaymentMethod]:
            raise ValueError("Invalid payment method")
        return v


class TransactionCreate(BaseModel):
    payment: PaymentCreate


class TransactionInDB(BaseModel):
    id: int
    user_id: int
    status: str  # Will be replaced with TransactionStatus enum
    subtotal: condecimal(ge=0, decimal_places=2)
    tax_amount: condecimal(ge=0, decimal_places=2)
    total_amount: condecimal(ge=0, decimal_places=2)
    payment_status: str  # Will be replaced with PaymentStatus enum
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReceiptRequest(BaseModel):
    email: Optional[str] = None
    print: bool = False
