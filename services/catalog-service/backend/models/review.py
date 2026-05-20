"""
Product review model.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint, func
from sqlalchemy.orm import relationship

from backend.database.base import Base


class ProductReview(Base):
    """Review left by a user for a product (menu item)."""
    __tablename__ = "product_reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("menu_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationship to the product
    product = relationship("MenuItem", backref="reviews")
