from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.database import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, nullable=True)
    discount_amount = Column(Integer, nullable=True)
    min_order_amount = Column(Integer, nullable=True, default=0)
    max_uses = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
