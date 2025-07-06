import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.repositories import payment_repo, transaction_repo
from app.db.session import get_db
from app.models.db_models import Payment, PaymentStatus, PaymentMethod
from app.services.exceptions import PaymentProcessingError

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db = db_session
    
    async def process_payment(
        self,
        transaction_id: int,
        payment_method: PaymentMethod,
        amount: float,
        payment_details: Dict[str, Any]
    ) -> Payment:
        """Process payment through appropriate gateway"""
        try:
            # In a real implementation, this would integrate with:
            # - Paystack for credit cards
            # - Square for mobile payments
            # - Cash drawer management for cash payments
            
            # For now, we'll simulate successful payment
            payment_data = {
                "transaction_id": transaction_id,
                "amount": amount,
                "method": payment_method,
                "status": PaymentStatus.COMPLETED,
                "processor_reference": "simulated_payment_123",
                "last_four_digits": payment_details.get("last_four", "1234"),
                "receipt_number": f"RCPT-{datetime.now().timestamp()}",
                "processed_at": datetime.utcnow()
            }
            
            payment = await payment_repo.create(self.db, obj_in=payment_data)
            
            # Update transaction status
            await transaction_repo.update(
                self.db,
                db_obj=await transaction_repo.get(self.db, id=transaction_id),
                obj_in={"payment_status": PaymentStatus.COMPLETED}
            )
            
            return payment
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            
            # Record failed payment attempt
            payment_data = {
                "transaction_id": transaction_id,
                "amount": amount,
                "method": payment_method,
                "status": PaymentStatus.FAILED,
                "processor_reference": None,
                "last_four_digits": payment_details.get("last_four", ""),
                "receipt_number": None,
                "processed_at": datetime.utcnow()
            }
            
            await payment_repo.create(self.db, obj_in=payment_data)
            
            # Update transaction status
            await transaction_repo.update(
                self.db,
                db_obj=await transaction_repo.get(self.db, id=transaction_id),
                obj_in={"payment_status": PaymentStatus.FAILED}
            )
            
            raise PaymentProcessingError(f"Payment processing failed: {str(e)}")

    async def refund_payment(
        self,
        payment_id: int,
        amount: Optional[float] = None
    ) -> Payment:
        """Process refund for a payment"""
        payment = await payment_repo.get(self.db, id=payment_id)
        if not payment:
            raise PaymentProcessingError("Payment not found")
        
        if payment.status != PaymentStatus.COMPLETED:
            raise PaymentProcessingError("Only completed payments can be refunded")
        
        refund_amount = amount if amount is not None else payment.amount
        
        try:
            # Simulate refund processing
            updated_payment = await payment_repo.update(
                self.db,
                db_obj=payment,
                obj_in={
                    "status": PaymentStatus.REFUNDED if refund_amount == payment.amount 
                            else PaymentStatus.PARTIALLY_REFUNDED
                }
            )
            
            return updated_payment
            
        except Exception as e:
            logger.error(f"Refund failed: {str(e)}")
            raise PaymentProcessingError(f"Refund processing failed: {str(e)}")
