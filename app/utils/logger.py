import logging
from typing import Any, Dict
from app.core.config import settings

def get_logger(name: str = None) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name or "app")
    return logger

def log_extra(**kwargs) -> Dict[str, Any]:
    """Create structured logging extra data"""
    return {"custom_fields": kwargs}

class RequestIdFilter(logging.Filter):
    """Add request_id to log records"""
    def __init__(self, request_id: str = None):
        super().__init__()
        self.request_id = request_id

    def filter(self, record):
        record.request_id = self.request_id
        return True
