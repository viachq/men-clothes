from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)


class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
