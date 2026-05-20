from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.enums import OrderStatus, PaymentMethod


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, default=OrderStatus.PENDING.value, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    delivery_address = Column(String, nullable=False)
    delivery_method = Column(String(50), default="nova_poshta", nullable=True)
    comment = Column(Text, nullable=True)
    payment_method = Column(String, default=PaymentMethod.CARD.value, nullable=False)
    total_price = Column(Integer, nullable=False, default=0)
    delivery_time = Column(DateTime, nullable=True)
    promo_code = Column(String(50), nullable=True)
    discount = Column(Integer, default=0, nullable=False)

    items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    user = relationship("User", backref="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Integer, nullable=False)

    product = relationship("MenuItem")
