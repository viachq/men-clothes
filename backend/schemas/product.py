from pydantic import BaseModel, Field
from typing import Optional


class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: int = Field(..., gt=0)
    old_price: Optional[int] = Field(None, gt=0)
    badge: Optional[str] = Field(None, max_length=20)
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[int] = Field(None, gt=0)
    old_price: Optional[int] = None
    badge: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class MenuItemRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: int
    old_price: Optional[int] = None
    badge: Optional[str] = None
    category_id: Optional[int]
    image_url: Optional[str]

    model_config = {"from_attributes": True}
