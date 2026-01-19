"""
Product model and related database schema.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database.base import Base


class MenuItem(Base):
    """Product model representing clothing items from the store."""
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # in cents/kopiyky
    image_url = Column(String, nullable=True)

    # Relationships
    category = relationship("Category", backref="menu_items")
