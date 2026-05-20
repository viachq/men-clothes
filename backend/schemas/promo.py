from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromoCodeCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    discount_percent: Optional[int] = Field(None, ge=1, le=100)
    discount_amount: Optional[int] = Field(None, gt=0)
    min_order_amount: Optional[int] = Field(0, ge=0)
    max_uses: Optional[int] = Field(None, gt=0)
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PromoCodeUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    discount_percent: Optional[int] = Field(None, ge=1, le=100)
    discount_amount: Optional[int] = Field(None, gt=0)
    min_order_amount: Optional[int] = Field(None, ge=0)
    max_uses: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PromoCodeOut(BaseModel):
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
    code: str = Field(..., min_length=1)
    order_total: int = Field(..., gt=0)


class PromoValidateResponse(BaseModel):
    valid: bool
    discount: int = 0
    message: str
