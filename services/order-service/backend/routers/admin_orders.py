from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.order import Order
from backend.deps import require_roles
from backend.core.enums import UserRole, OrderStatus


router = APIRouter(prefix="/admin/orders", tags=["admin:orders"])


@router.get("")
def list_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER))
):
    """Get all orders (admin only)."""
    q = db.query(Order)
    
    if status is not None:
        q = q.filter(Order.status == status)
    
    orders = q.all()
    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "status": o.status,
            "total_price": o.total_price,
            "delivery_address": o.delivery_address,
            "delivery_time": o.delivery_time.isoformat() if o.delivery_time else None,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ]


@router.get("/{order_id}")
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER))
):
    """Get detailed order information including order items (admin only)."""
    from backend.models.order_item import OrderItem
    from backend.clients.catalog_client import get_catalog_client
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order items from local DB
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    # Get menu item names from catalog-service via HTTP
    catalog_client = get_catalog_client()
    items_data = []
    for item in order_items:
        menu_item_name = "Unknown"
        try:
            menu_item = catalog_client.get_product(item.menu_item_id)
            menu_item_name = menu_item.get("name", "Unknown")
        except HTTPException:
            pass  # Keep "Unknown" if menu item not found
        
        items_data.append({
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "menu_item_name": menu_item_name,
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": item.price * item.quantity
        })
    
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "delivery_address": order.delivery_address,
        "payment_method": order.payment_method,
        "total_price": order.total_price,
        "delivery_time": order.delivery_time.isoformat() if order.delivery_time else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        "items": items_data
    }


@router.put("/{order_id}/status")
def set_status(order_id: int, status: str, db: Session = Depends(get_db), _: object = Depends(require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER))):
    """Update order status. Allowed values: pending, delivering, delivered, cancelled."""
    allowed = [s.value for s in OrderStatus]
    if status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {allowed}",
        )
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    o.status = status
    db.commit()
    return {"message": "Status updated", "id": o.id, "status": o.status}




