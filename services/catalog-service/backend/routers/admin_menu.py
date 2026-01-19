"""
Admin product management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.menu_item import MenuItem
from backend.deps import require_roles
from backend.core.enums import UserRole
from backend.schemas.menu import MenuItemCreate, MenuItemUpdate, MenuItemRead


router = APIRouter(prefix="/admin/products", tags=["admin:products"])


@router.post("", response_model=MenuItemRead)
def create_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER))
):
    """Create product."""
    item = MenuItem(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category_id=payload.category_id,
        image_url=payload.image_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Clear cache for products after create
    from backend.routers.menu import clear_products_cache
    clear_products_cache()
    
    return item


@router.put("/{item_id}", response_model=MenuItemRead)
def update_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER))
):
    """Update menu item."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    if payload.name is not None:
        item.name = payload.name
    if payload.description is not None:
        item.description = payload.description
    if payload.price is not None:
        item.price = payload.price
    if payload.category_id is not None:
        item.category_id = payload.category_id
    if payload.image_url is not None:
        item.image_url = payload.image_url
    
    db.commit()
    db.refresh(item)
    
    # Clear cache for products after update
    from backend.routers.menu import clear_products_cache
    clear_products_cache()
    
    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER))
):
    """Delete menu item."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    db.delete(item)
    db.commit()
    
    # Clear cache for products after delete
    from backend.routers.menu import clear_products_cache
    clear_products_cache()
    
    return {"message": "Menu item deleted"}
