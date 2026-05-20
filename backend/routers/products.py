import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.product import MenuItem
from backend.deps import require_roles
from backend.enums import UserRole
from backend.schemas.product import MenuItemCreate, MenuItemUpdate, MenuItemRead

router = APIRouter(tags=["products"])

_cache = None
_cache_time = 0.0


def _clear_cache():
    global _cache, _cache_time
    _cache = None
    _cache_time = 0.0


@router.get("/products/")
def get_all_products(
    q: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    global _cache, _cache_time
    if not q and category_id is None:
        now = time.time()
        if _cache is None or (now - _cache_time) > 60:
            _cache = db.query(MenuItem).all()
            _cache_time = now
        items = _cache
    else:
        query = db.query(MenuItem)
        if q:
            query = query.filter(MenuItem.name.like(f"%{q}%"))
        if category_id is not None:
            query = query.filter(MenuItem.category_id == category_id)
        items = query.all()

    return [
        {
            "id": i.id, "name": i.name, "description": i.description,
            "price": i.price, "old_price": i.old_price, "badge": i.badge,
            "category_id": i.category_id, "image_url": i.image_url,
        }
        for i in items
    ]


@router.get("/products/{item_id}")
def get_product(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": item.id, "name": item.name, "description": item.description,
        "price": item.price, "old_price": item.old_price, "badge": item.badge,
        "category_id": item.category_id, "image_url": item.image_url,
    }


# ── Admin ────────────────────────────────────────────────────────────

@router.post("/admin/products", response_model=MenuItemRead, status_code=201)
def create_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    item = MenuItem(
        name=payload.name, description=payload.description,
        price=payload.price, old_price=payload.old_price, badge=payload.badge,
        category_id=payload.category_id, image_url=payload.image_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    _clear_cache()
    return item


@router.put("/admin/products/{item_id}", response_model=MenuItemRead)
def update_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
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
    if payload.old_price is not None:
        item.old_price = payload.old_price
    if payload.badge is not None:
        item.badge = payload.badge
    if payload.image_url is not None:
        item.image_url = payload.image_url
    db.commit()
    db.refresh(item)
    _clear_cache()
    return item


@router.delete("/admin/products/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    _clear_cache()
