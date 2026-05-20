"""
Pydantic schemas for product variants (size + stock).
"""
from pydantic import BaseModel, Field


class VariantCreate(BaseModel):
    """Schema for creating a product variant."""
    size: str = Field(..., min_length=1, max_length=10, description="Size label (S, M, L, XL, XXL)")
    stock: int = Field(..., ge=0, description="Stock quantity")


class VariantUpdate(BaseModel):
    """Schema for updating variant stock."""
    stock: int = Field(..., ge=0, description="New stock quantity")


class VariantOut(BaseModel):
    """Schema for variant response."""
    id: int
    menu_item_id: int
    size: str
    stock: int

    model_config = {"from_attributes": True}
