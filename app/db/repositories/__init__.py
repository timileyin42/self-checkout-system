from ..session import session_manager

from .product import ProductRepository
from .cart import CartRepository
from .inventory import InventoryRepository
from .transaction import TransactionRepository
from .payment import PaymentRepository
from .user import UserRepository

# Initialize repositories
product_repo = ProductRepository()
cart_repo = CartRepository()
inventory_repo = InventoryRepository()
transaction_repo = TransactionRepository()
payment_repo = PaymentRepository()
user_repo = UserRepository()

__all__ = [
    "session_manager",
    "product_repo",
    "cart_repo",
    "inventory_repo",
    "transaction_repo",
    "payment_repo",
    "user_repo"
]
