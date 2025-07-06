from typing import Any, Optional
from pydantic import BaseModel, validator
import re

class BaseValidator(BaseModel):
    """Base validator with common validation methods"""
    
    @validator("*", pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

def validate_barcode(barcode: str) -> str:
    """Validate barcode format"""
    if not re.match(r'^[0-9]{8,14}$', barcode):
        raise ValueError("Invalid barcode format")
    return barcode

def validate_price(price: float) -> float:
    """Validate price is positive and reasonable"""
    if price <= 0:
        raise ValueError("Price must be positive")
    if price > 1_000_000:  # $1M max price
        raise ValueError("Price exceeds maximum allowed value")
    return round(price, 2)

def validate_age_restriction(age_restriction: Optional[str]) -> Optional[str]:
    """Validate age restriction values"""
    if age_restriction and age_restriction not in ["none", "18+", "21+"]:
        raise ValueError("Invalid age restriction value")
    return age_restriction
