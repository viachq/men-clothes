from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.order import Order, OrderItem
from backend.models.payment import Payment
from backend.models.cart import Cart
from backend.models.product import MenuItem
from backend.models.promo_code import PromoCode
from backend.deps import get_current_user, require_roles
from backend.enums import UserRole, OrderStatus, PaymentMethod, PaymentStatus
from backend.schemas.order import OrderCreate
from backend.routers.promocodes import _validate_promo

router = APIRouter(tags=["orders"])


# ── Client endpoints ─────────────────────────────────────────────────

@router.post("/orders", status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = sum(item.price * item.quantity for item in cart.items)

    promo_code_str = None
    discount = 0
    if payload.promo_code:
        valid, disc, message = _validate_promo(db, payload.promo_code, total_price)
        if not valid:
            raise HTTPException(status_code=400, detail=message)
        promo_code_str = payload.promo_code.upper()
        discount = disc
        total_price -= discount

    delivery_datetime = None
    if payload.delivery_time:
        try:
            delivery_datetime = datetime.fromisoformat(payload.delivery_time.replace("Z", "+00:00"))
            if delivery_datetime <= datetime.utcnow():
                raise HTTPException(status_code=400, detail="Delivery time must be in the future")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid delivery_time format")

    order = Order(
        user_id=current_user.id,
        name=payload.name,
        surname=payload.surname,
        phone=payload.phone,
        email=payload.email,
        delivery_address=payload.address,
        delivery_method=payload.delivery_method or "nova_poshta",
        comment=payload.comment,
        payment_method=payload.payment_method or PaymentMethod.CARD.value,
        total_price=total_price,
        delivery_time=delivery_datetime,
        status=OrderStatus.PENDING.value,
        promo_code=promo_code_str,
        discount=discount,
    )
    db.add(order)
    db.flush()

    for cart_item in cart.items:
        db.add(OrderItem(
            order_id=order.id,
            menu_item_id=cart_item.menu_item_id,
            quantity=cart_item.quantity,
            price=cart_item.price,
        ))

    if promo_code_str:
        promo = db.query(PromoCode).filter(PromoCode.code == promo_code_str).first()
        if promo:
            promo.current_uses += 1

    for item in list(cart.items):
        db.delete(item)

    db.commit()
    db.refresh(order)

    payment = Payment(order_id=order.id, amount=total_price, status=PaymentStatus.PENDING.value)
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Order created",
        "id": order.id,
        "status": order.status,
        "total_price": order.total_price,
        "name": order.name, "surname": order.surname,
        "phone": order.phone, "email": order.email,
        "delivery_address": order.delivery_address,
        "delivery_method": order.delivery_method,
        "comment": order.comment,
        "delivery_time": order.delivery_time.isoformat() if order.delivery_time else None,
        "payment_method": order.payment_method,
        "payment_id": payment.id,
        "promo_code": order.promo_code,
        "discount": order.discount,
    }


@router.put("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
    order.status = OrderStatus.CANCELLED.value
    db.commit()
    db.refresh(order)
    return {"message": "Order cancelled", "id": order.id, "status": order.status}


@router.get("/orders")
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return [
        {
            "id": o.id, "status": o.status, "total_price": o.total_price,
            "name": o.name, "surname": o.surname, "phone": o.phone, "email": o.email,
            "delivery_address": o.delivery_address, "delivery_method": o.delivery_method,
            "comment": o.comment,
            "delivery_time": o.delivery_time.isoformat() if o.delivery_time else None,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "payment_method": o.payment_method,
            "promo_code": o.promo_code, "discount": o.discount,
        }
        for o in orders
    ]


# ── Admin endpoints ──────────────────────────────────────────────────

@router.get("/admin/orders")
def admin_list_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    q = db.query(Order)
    if status is not None:
        q = q.filter(Order.status == status)
    orders = q.all()
    return [
        {
            "id": o.id, "user_id": o.user_id, "status": o.status,
            "total_price": o.total_price, "delivery_address": o.delivery_address,
            "delivery_time": o.delivery_time.isoformat() if o.delivery_time else None,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


@router.get("/admin/orders/{order_id}")
def admin_get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items_data = []
    for item in order.items:
        product = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        items_data.append({
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "menu_item_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": item.price * item.quantity,
        })

    return {
        "id": order.id, "user_id": order.user_id, "status": order.status,
        "name": order.name, "surname": order.surname,
        "phone": order.phone, "email": order.email,
        "delivery_address": order.delivery_address,
        "delivery_method": order.delivery_method,
        "comment": order.comment,
        "payment_method": order.payment_method,
        "total_price": order.total_price,
        "promo_code": order.promo_code, "discount": order.discount,
        "delivery_time": order.delivery_time.isoformat() if order.delivery_time else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        "items": items_data,
    }


@router.put("/admin/orders/{order_id}/status")
def admin_set_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)),
):
    allowed = [s.value for s in OrderStatus]
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed}")
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    o.status = status
    db.commit()
    return {"message": "Status updated", "id": o.id, "status": o.status}
