from pydantic import BaseModel, Field
from typing import Optional


class OrderCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    surname: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    address: str = Field(..., min_length=5, max_length=200)
    delivery_method: Optional[str] = Field("nova_poshta", max_length=50)
    comment: Optional[str] = Field(None, max_length=1000)
    delivery_time: Optional[str] = None
    payment_method: Optional[str] = Field("card", max_length=20)
    promo_code: Optional[str] = Field(None, max_length=50)
