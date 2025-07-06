from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.repositories import transaction_repo
from app.db.session import get_db
from app.models.db_models import Transaction
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("app", "templates/receipts"),
    autoescape=select_autoescape()
)

class ReceiptService:
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db = db_session

    async def generate_receipt_data(self, transaction_id: int) -> Dict[str, Any]:
        """Prepare all data needed for receipt generation"""
        transaction = await transaction_repo.get_with_items(
            self.db,
            transaction_id=transaction_id
        )
        
        if not transaction:
            raise ValueError("Transaction not found")
        
        return {
            "transaction": transaction,
            "receipt_number": transaction.payments[0].receipt_number,
            "date": transaction.completed_at or datetime.utcnow(),
            "store_info": {
                "name": "Self-Checkout System",
                "address": "123 Retail Ave, Tech City",
                "phone": "(555) 123-4567"
            },
            "payment_method": transaction.payment_method,
            "items": [
                {
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "total": item.quantity * item.price
                }
                for item in transaction.items
            ],
            "subtotal": transaction.subtotal,
            "tax": transaction.tax_amount,
            "total": transaction.total_amount
        }

    async def generate_receipt_html(self, transaction_id: int) -> str:
        """Generate HTML receipt"""
        data = await self.generate_receipt_data(transaction_id)
        template = env.get_template("receipt.html")
        return template.render(**data)

    async def generate_receipt_text(self, transaction_id: int) -> str:
        """Generate plain text receipt"""
        data = await self.generate_receipt_data(transaction_id)
        template = env.get_template("receipt.txt")
        return template.render(**data)

    async def send_receipt_email(self, transaction_id: int, email: str) -> bool:
        """Send receipt via email (mock implementation)"""
        html_content = await self.generate_receipt_html(transaction_id)
        # In real implementation, integrate with email service
        print(f"Would send receipt to {email} with content:\n{html_content}")
        return True

    async def print_receipt(self, transaction_id: int) -> bool:
        """Print receipt (mock implementation)"""
        text_content = await self.generate_receipt_text(transaction_id)
        # In real implementation, integrate with printer service
        print(f"Would print receipt:\n{text_content}")
        return True
