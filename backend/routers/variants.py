from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.enums import UserRole
from backend.models.variant import ProductVariant
from backend.models.product import MenuItem
from backend.schemas.variant import VariantCreate, VariantUpdate, VariantOut

router = APIRouter(prefix="/variants", tags=["variants"])


@router.get("/product/{product_id}", response_model=list[VariantOut])
def list_variants(product_id: int, db: Session = Depends(get_db)):
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db.query(ProductVariant).filter(ProductVariant.menu_item_id == product_id).order_by(ProductVariant.id).all()


@router.post("/product/{product_id}", response_model=VariantOut, status_code=201)
def create_variant(
    product_id: int,
    body: VariantCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    existing = db.query(ProductVariant).filter(
        ProductVariant.menu_item_id == product_id,
        ProductVariant.size == body.size.upper(),
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Variant with size '{body.size.upper()}' already exists for this product")
    variant = ProductVariant(menu_item_id=product_id, size=body.size.upper(), stock=body.stock)
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


@router.put("/{variant_id}", response_model=VariantOut)
def update_variant(
    variant_id: int,
    body: VariantUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    variant.stock = body.stock
    db.commit()
    db.refresh(variant)
    return variant


@router.delete("/{variant_id}", status_code=204)
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    db.delete(variant)
    db.commit()
