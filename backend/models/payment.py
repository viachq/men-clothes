from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from backend.database import Base
from backend.enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String, default=PaymentStatus.PENDING.value, nullable=False, index=True)
    transaction_id = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
