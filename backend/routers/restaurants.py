"""
Restaurant endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.restaurant import Restaurant
from backend.models.review import Review
from backend.core.config import DEFAULT_RESTAURANT_ID


router = APIRouter(prefix="/restaurant", tags=["restaurant"])


@router.get("/info")
def get_restaurant_info(db: Session = Depends(get_db)):
    """Get information about our restaurant."""
    r = db.query(Restaurant).filter(Restaurant.id == DEFAULT_RESTAURANT_ID).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return {
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "address": r.address,
        "phone": r.phone,
        "opening_hours": r.opening_hours,
    }


@router.get("/reviews")
def get_restaurant_reviews(db: Session = Depends(get_db)):
    """Get all reviews for our restaurant."""
    # All reviews are for our restaurant (via orders)
    reviews = db.query(Review).order_by(Review.created_at.desc()).all()
    return [
        {
            "id": rv.id,
            "user_id": rv.user_id,
            "order_id": rv.order_id,
            "rating": rv.rating,
            "text": rv.text,
            "created_at": rv.created_at.isoformat() if rv.created_at else None
        }
        for rv in reviews
    ]
