"""
Product variant endpoints for size and stock management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user, require_roles
from backend.core.enums import UserRole
from backend.models.product_variant import ProductVariant
from backend.models.menu_item import MenuItem
from backend.schemas.variant import VariantCreate, VariantUpdate, VariantOut

router = APIRouter(prefix="/variants", tags=["variants"])


@router.get("/product/{product_id}", response_model=list[VariantOut])
def list_variants(
    product_id: int,
    db: Session = Depends(get_db),
):
    """List all variants (sizes) for a product. Public endpoint."""
    # Verify product exists
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    variants = (
        db.query(ProductVariant)
        .filter(ProductVariant.menu_item_id == product_id)
        .order_by(ProductVariant.id)
        .all()
    )
    return variants


@router.post(
    "/product/{product_id}",
    response_model=VariantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_variant(
    product_id: int,
    body: VariantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    """Create a new variant for a product. Admin/Manager only."""
    # Verify product exists
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Check for duplicate size
    existing = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.menu_item_id == product_id,
            ProductVariant.size == body.size.upper(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Variant with size '{body.size.upper()}' already exists for this product",
        )

    variant = ProductVariant(
        menu_item_id=product_id,
        size=body.size.upper(),
        stock=body.stock,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


@router.put("/{variant_id}", response_model=VariantOut)
def update_variant(
    variant_id: int,
    body: VariantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    """Update variant stock. Admin/Manager only."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found",
        )

    variant.stock = body.stock
    db.commit()
    db.refresh(variant)
    return variant


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    """Delete a variant. Admin/Manager only."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found",
        )

    db.delete(variant)
    db.commit()
