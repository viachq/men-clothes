from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models.product import MenuItem
from backend.models.review import ProductReview
from backend.models.order import Order, OrderItem
from backend.models.user import User
from backend.enums import UserRole, OrderStatus
from backend.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ProductReview)
        .filter(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
        .all()
    )


def _has_purchased(db: Session, user_id: int, product_id: int) -> bool:
    return (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.DELIVERED.value,
            OrderItem.menu_item_id == product_id,
        )
        .first()
    ) is not None


@router.get("/can-review/{product_id}")
def can_review(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        return {"can_review": False, "reason": "product_not_found"}
    existing = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.user_id == current_user.id,
    ).first()
    if existing:
        return {"can_review": False, "reason": "already_reviewed"}
    if not _has_purchased(db, current_user.id, product_id):
        return {"can_review": False, "reason": "not_purchased"}
    return {"can_review": True}


@router.post("/product/{product_id}", response_model=ReviewOut, status_code=201)
def create_review(
    product_id: int,
    body: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    existing = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    if not _has_purchased(db, current_user.id, product_id):
        raise HTTPException(status_code=403, detail="You can only review products you have purchased and received")
    review = ProductReview(
        product_id=product_id,
        user_id=current_user.id,
        username=current_user.username,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(ProductReview).filter(ProductReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    is_admin = current_user.role in (UserRole.MANAGER.value, UserRole.SYSTEM_ADMIN.value)
    if review.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    db.delete(review)
    db.commit()
