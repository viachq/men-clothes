"""
PromoCode model for promotional discount codes.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database.base import Base


class PromoCode(Base):
    """Promotional code model for order discounts."""
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, nullable=True)          # e.g. 10 means 10%
    discount_amount = Column(Integer, nullable=True)            # fixed amount in cents/kopiyky
    min_order_amount = Column(Integer, nullable=True, default=0)  # minimum order total to apply
    max_uses = Column(Integer, nullable=True)                   # None = unlimited
    current_uses = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
