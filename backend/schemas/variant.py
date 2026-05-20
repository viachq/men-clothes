from pydantic import BaseModel, Field


class VariantCreate(BaseModel):
    size: str = Field(..., min_length=1, max_length=10)
    stock: int = Field(0, ge=0)


class VariantUpdate(BaseModel):
    stock: int = Field(..., ge=0)


class VariantOut(BaseModel):
    id: int
    menu_item_id: int
    size: str
    stock: int

    model_config = {"from_attributes": True}
