from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.category import Category
from backend.models.menu_item import MenuItem


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).all()
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cats]


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    c = db.query(Category).filter(Category.id == category_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"id": c.id, "name": c.name, "description": c.description}


# Removed - MenuItem doesn't have category_id in simplified version
# @router.get("/{category_id}/items")
# def get_category_items(category_id: int, db: Session = Depends(get_db)):
#     # This endpoint is disabled in single-restaurant mode
#     pass


