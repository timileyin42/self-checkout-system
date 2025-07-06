class ServiceException(Exception):
    """Base exception for service layer errors"""
    pass

class InsufficientStockError(ServiceException):
    """Raised when there isn't enough inventory"""
    def __init__(self, product_id: int, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for product {product_id}. "
            f"Available: {available}, Requested: {requested}"
        )

class AgeVerificationError(ServiceException):
    """Raised when age verification fails"""
    pass

class PaymentProcessingError(ServiceException):
    """Raised when payment processing fails"""
    pass

class CartValidationError(ServiceException):
    """Raised when cart validation fails"""
    pass
