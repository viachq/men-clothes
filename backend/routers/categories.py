import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.category import Category
from backend.deps import require_roles
from backend.enums import UserRole
from backend.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead

router = APIRouter(tags=["categories"])

_cache = None
_cache_time = 0.0


def _clear_cache():
    global _cache, _cache_time
    _cache = None
    _cache_time = 0.0


@router.get("/categories/")
def list_categories(db: Session = Depends(get_db)):
    global _cache, _cache_time
    now = time.time()
    if _cache is None or (now - _cache_time) > 300:
        _cache = db.query(Category).all()
        _cache_time = now
    return [{"id": c.id, "name": c.name} for c in _cache]


@router.post("/admin/categories", response_model=CategoryRead, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    if db.query(Category).filter(Category.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Category name already exists")
    c = Category(name=payload.name)
    db.add(c)
    db.commit()
    db.refresh(c)
    _clear_cache()
    return c


@router.put("/admin/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    c = db.query(Category).filter(Category.id == category_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        c.name = payload.name
    db.commit()
    db.refresh(c)
    _clear_cache()
    return c


@router.delete("/admin/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    c = db.query(Category).filter(Category.id == category_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(c)
    db.commit()
    _clear_cache()
