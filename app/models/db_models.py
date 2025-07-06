from enum import Enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, 
    DateTime, ForeignKey, Enum as SQLAlchemyEnum,
    Numeric, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, validates
from app.db.base import Base  # SQLAlchemy Base class


class UserRole(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"


class ProductCategory(str, Enum):
    GROCERY = "grocery"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    PHARMACY = "pharmacy"
    ALCOHOL = "alcohol"
    OTHER = "other"


class ProductStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"
    RECALLED = "recalled"


class AgeRestriction(str, Enum):
    NONE = "none"
    AGE_18 = "18+"
    AGE_21 = "21+"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"
    MOBILE_PAY = "mobile_pay"
    GIFT_CARD = "gift_card"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class TransactionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class Product(Base):
    """Inventory product model with pricing and restrictions"""
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint('current_price > 0', name='positive_price'),
        UniqueConstraint('barcode', name='unique_barcode'),
    )

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(50), unique=True, nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category = Column(SQLAlchemyEnum(ProductCategory), nullable=False)
    status = Column(SQLAlchemyEnum(ProductStatus), default=ProductStatus.ACTIVE)
    age_restriction = Column(SQLAlchemyEnum(AgeRestriction), default=AgeRestriction.NONE)
    current_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    tax_rate = Column(Numeric(5, 4), default=0.0)  # 0.0875 for 8.75%
    requires_serial_number = Column(Boolean, default=False)
    is_weighted = Column(Boolean, default=False)
    min_age_verification = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory = relationship("Inventory", back_populates="product", uselist=False)
    cart_items = relationship("CartItem", back_populates="product")
    transaction_items = relationship("TransactionItem", back_populates="product")

    @validates('tax_rate')
    def validate_tax_rate(self, key, tax_rate):
        if not 0 <= tax_rate <= 1:
            raise ValueError("Tax rate must be between 0 and 1")
        return tax_rate


class Inventory(Base):
    """Real-time stock level tracking"""
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='non_negative_quantity'),
        CheckConstraint('reorder_threshold >= 0', name='non_negative_reorder'),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    reorder_threshold = Column(Integer, default=5)
    last_restocked = Column(DateTime)
    next_restock_estimate = Column(DateTime)
    is_active = Column(Boolean, default=True)

    product = relationship("Product", back_populates="inventory")


class User(Base):
    """System users (customers and staff)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default=UserRole.CUSTOMER.value)
    date_of_birth = Column(DateTime)  # For age verification
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    carts = relationship("Cart", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Cart(Base):
    """Shopping cart for active session"""
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(100), index=True)  # For guest users
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    """Individual items in a shopping cart"""
    __tablename__ = "cart_items"
    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
        UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
    )

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price_at_addition = Column(Numeric(10, 2))  # Snapshot of price
    added_at = Column(DateTime, default=datetime.utcnow)
    is_age_verified = Column(Boolean, default=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity


class Transaction(Base):
    """Completed purchase transaction"""
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='non_negative_amount'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cart_id = Column(Integer, ForeignKey("carts.id"))
    status = Column(SQLAlchemyEnum(TransactionStatus), default=TransactionStatus.COMPLETED)
    subtotal = Column(Numeric(10, 2))
    tax_amount = Column(Numeric(10, 2))
    total_amount = Column(Numeric(10, 2))
    payment_method = Column(SQLAlchemyEnum(PaymentMethod))
    payment_status = Column(SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="transactions")
    cart = relationship("Cart")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    """Snapshot of purchased items"""
    __tablename__ = "transaction_items"
    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
        CheckConstraint('price > 0', name='positive_price'),
    )

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Numeric(10, 2))
    tax_rate = Column(Numeric(5, 4))
    was_age_verified = Column(Boolean, default=False)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")


class Payment(Base):
    """Payment information and processing"""
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_amount'),
    )

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    amount = Column(Numeric(10, 2))
    method = Column(SQLAlchemyEnum(PaymentMethod))
    status = Column(SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.PENDING)
    processor_reference = Column(String(100))  # Payment gateway ID
    last_four_digits = Column(String(4))  # For card payments
    receipt_number = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    transaction = relationship("Transaction", back_populates="payments")


class SystemLog(Base):
    """Audit logging for security and troubleshooting"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    event_data = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(45))
    user_agent = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
