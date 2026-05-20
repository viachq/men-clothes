"""
Product reviews endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models.menu_item import MenuItem
from backend.models.review import ProductReview
from backend.models.user import User
from backend.core.enums import UserRole
from backend.schemas.review import ReviewCreate, ReviewOut


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a product (public endpoint)."""
    reviews = (
        db.query(ProductReview)
        .filter(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
        .all()
    )
    return reviews


@router.get("/can-review/{product_id}")
def can_review(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check whether the current user is allowed to review a product."""
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        return {"can_review": False}

    # User cannot review the same product twice
    existing = (
        db.query(ProductReview)
        .filter(
            ProductReview.product_id == product_id,
            ProductReview.user_id == current_user.id,
        )
        .first()
    )
    return {"can_review": existing is None}


@router.post("/product/{product_id}", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    product_id: int,
    body: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a review for a product (authenticated users only, one review per product)."""
    product = db.query(MenuItem).filter(MenuItem.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    existing = (
        db.query(ProductReview)
        .filter(
            ProductReview.product_id == product_id,
            ProductReview.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product",
        )

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


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a review. Users can delete their own reviews; admins can delete any."""
    review = db.query(ProductReview).filter(ProductReview.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    is_admin = current_user.role in (UserRole.MANAGER.value, UserRole.SYSTEM_ADMIN.value)
    if review.user_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review",
        )

    db.delete(review)
    db.commit()
