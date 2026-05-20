"""
Promo code Pydantic v2 schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromoCodeCreate(BaseModel):
    """Schema for creating a new promo code."""
    code: str = Field(..., min_length=2, max_length=50, description="Unique promo code string")
    discount_percent: Optional[int] = Field(None, ge=1, le=100, description="Discount percentage (1-100)")
    discount_amount: Optional[int] = Field(None, gt=0, description="Fixed discount in kopiyky/cents")
    min_order_amount: Optional[int] = Field(0, ge=0, description="Minimum order total to apply promo")
    max_uses: Optional[int] = Field(None, gt=0, description="Maximum number of uses (null = unlimited)")
    is_active: bool = Field(True, description="Whether the promo code is active")
    valid_from: Optional[datetime] = Field(None, description="Start of validity period")
    valid_until: Optional[datetime] = Field(None, description="End of validity period")


class PromoCodeUpdate(BaseModel):
    """Schema for updating an existing promo code."""
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    discount_percent: Optional[int] = Field(None, ge=1, le=100)
    discount_amount: Optional[int] = Field(None, gt=0)
    min_order_amount: Optional[int] = Field(None, ge=0)
    max_uses: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PromoCodeOut(BaseModel):
    """Schema for promo code response."""
    id: int
    code: str
    discount_percent: Optional[int] = None
    discount_amount: Optional[int] = None
    min_order_amount: Optional[int] = None
    max_uses: Optional[int] = None
    current_uses: int
    is_active: bool
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PromoValidateRequest(BaseModel):
    """Schema for validating a promo code against an order total."""
    code: str = Field(..., min_length=1, description="Promo code to validate")
    order_total: int = Field(..., gt=0, description="Order total in kopiyky/cents")


class PromoValidateResponse(BaseModel):
    """Schema for promo code validation result."""
    valid: bool
    discount: int = 0
    message: str
