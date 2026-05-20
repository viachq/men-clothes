from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True)
    size = Column(String(10), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("menu_item_id", "size", name="uq_variant_product_size"),
    )

    product = relationship("MenuItem", backref="variants")
