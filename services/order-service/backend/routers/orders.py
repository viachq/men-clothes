"""
Order management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend.models.user import User
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.payment import Payment
from backend.models.cart import Cart
from backend.models.promo_code import PromoCode
from backend.deps import get_current_user
from backend.core.enums import OrderStatus, PaymentMethod, PaymentStatus
from backend.schemas.order import OrderCreate
from backend.routers.promocodes import _validate_promo

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=201)
async def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order from cart.
    
    - Payment method is always CARD (as per requirements)
    - Delivery time is optional (for scheduling future orders)
    - Cart must not be empty
    """
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    total_price = sum(item.price * item.quantity for item in cart.items)

    # Apply promo code if provided
    promo_code_str = None
    discount = 0
    if payload.promo_code:
        valid, disc, message = _validate_promo(db, payload.promo_code, total_price)
        if not valid:
            raise HTTPException(status_code=400, detail=message)
        promo_code_str = payload.promo_code.upper()
        discount = disc
        total_price = total_price - discount

    # Parse and validate delivery_time if provided
    delivery_datetime = None
    if payload.delivery_time:
        try:
            delivery_datetime = datetime.fromisoformat(payload.delivery_time.replace('Z', '+00:00'))
            # Validate that delivery time is in the future
            if delivery_datetime <= datetime.utcnow():
                raise HTTPException(
                    status_code=400,
                    detail="Delivery time must be in the future"
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid delivery_time format. Use ISO format (e.g., '2024-12-25T18:00:00')"
            )
    
    # Create order - payment is ALWAYS card (as per requirements)
    order = Order(
        user_id=current_user.id,
        delivery_address=payload.address,
        payment_method=PaymentMethod.CARD.value,  # Always card payment
        total_price=total_price,
        delivery_time=delivery_datetime,
        status=OrderStatus.PENDING.value,
        promo_code=promo_code_str,
        discount=discount,
    )

    db.add(order)
    db.flush()

    # Create order items
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=cart_item.menu_item_id,
            quantity=cart_item.quantity,
            price=cart_item.price
        )
        db.add(order_item)

    # Increment promo code usage
    if promo_code_str:
        promo = db.query(PromoCode).filter(PromoCode.code == promo_code_str).first()
        if promo:
            promo.current_uses += 1

    # Clear cart
    for item in list(cart.items):
        db.delete(item)

    db.commit()
    db.refresh(order)
    
    # Створюємо Payment запис зі статусом PENDING
    payment = Payment(
        order_id=order.id,
        amount=total_price,
        status=PaymentStatus.PENDING.value
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {
        "message": "Order created",
        "id": order.id,
        "status": order.status,
        "total_price": order.total_price,
        "delivery_address": order.delivery_address,
        "delivery_time": order.delivery_time.isoformat() if order.delivery_time else None,
        "payment_method": order.payment_method,
        "payment_id": payment.id,
        "promo_code": order.promo_code,
        "discount": order.discount,
    }


@router.put("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel an order. Only the order owner can cancel, and only if status is PENDING.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be cancelled",
        )

    order.status = OrderStatus.CANCELLED.value
    db.commit()
    db.refresh(order)

    return {
        "message": "Order cancelled",
        "id": order.id,
        "status": order.status,
    }


@router.get("")
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get my orders."""
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    
    return [
        {
            "id": o.id,
            "status": o.status,
            "total_price": o.total_price,
            "delivery_address": o.delivery_address,
            "delivery_time": o.delivery_time.isoformat() if o.delivery_time else None,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "payment_method": o.payment_method,
            "promo_code": o.promo_code,
            "discount": o.discount,
        }
        for o in orders
    ]


