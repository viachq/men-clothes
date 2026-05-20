from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    username: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
