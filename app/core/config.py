import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, field_validator
from typing import Optional, Dict, Any

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Self-Checkout System"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str 
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_POOL_MAX_OVERFLOW: int = 10
    
    # Security
    SECRET_KEY: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    ALGORITHM: str = "HS256"
    
    # Payment
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYSTACK_BASE_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


    @field_validator("DATABASE_URL")
    def validate_db_url(cls, v):
        if isinstance(v, str):
            # Ensure proper format for asyncpg
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            # Handle URL-encoded passwords
            if '%40' in v:
                v = v.replace('%40', '@')
        return v

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
