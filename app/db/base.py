from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import Column, DateTime
from datetime import datetime


Base = declarative_base()

@declarative_mixin
class TimestampMixin:
    """Mixin that adds timestamp columns to models"""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
