"""
Category-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreate(BaseModel):
    """Category creation schema."""
    name: str = Field(..., min_length=2, max_length=50, description="Category name")


class CategoryUpdate(BaseModel):
    """Category update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)


class CategoryRead(BaseModel):
    """Category response schema."""
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "name": "Polo Shirts"
            }]
        }
    }
