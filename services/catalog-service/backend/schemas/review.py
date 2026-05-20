"""
Pydantic schemas for product reviews.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=2000, description="Optional review text")


class ReviewOut(BaseModel):
    """Schema for returning a review."""
    id: int
    product_id: int
    user_id: int
    username: str
    rating: int
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
