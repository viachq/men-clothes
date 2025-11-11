"""
Order model and related database schema.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database.base import Base
from backend.core.enums import OrderStatus, PaymentMethod


class Order(Base):
    """Order model representing customer orders."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant_info.id"), nullable=False, index=True)
    status = Column(String, default=OrderStatus.PENDING.value, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Order details
    delivery_address = Column(String, nullable=False)
    payment_method = Column(String, default=PaymentMethod.CARD.value, nullable=False)
    total_price = Column(Integer, nullable=False, default=0)  # in cents/kopiyky
    delivery_time = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="orders")
    restaurant = relationship("Restaurant", backref="orders")
