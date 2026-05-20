"""
Product variant model for size + stock tracking.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database.base import Base


class ProductVariant(Base):
    """Product variant representing a specific size with stock quantity."""
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("menu_item_id", "size", name="uq_product_size"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_item_id = Column(
        Integer,
        ForeignKey("menu_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    size = Column(String(10), nullable=False)  # S, M, L, XL, XXL
    stock = Column(Integer, default=0, nullable=False)

    product = relationship("MenuItem", backref="variants")
