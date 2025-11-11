"""
Admin statistics endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.menu_item import MenuItem
from backend.core.config import DEFAULT_RESTAURANT_ID


router = APIRouter(prefix="/admin/stats", tags=["admin:stats"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    """Statistics for default restaurant."""
    # All orders for default restaurant
    orders = db.query(Order).filter(Order.restaurant_id == DEFAULT_RESTAURANT_ID).all()
    orders_count = len(orders)
    revenue = sum(o.total_price for o in orders)
    
    # Average order value
    average_order = revenue // orders_count if orders_count > 0 else 0
    
    # Active orders (not delivered or cancelled)
    active_statuses = ['pending', 'accepted', 'preparing', 'ready', 'delivering']
    active_orders = db.query(Order)\
        .filter(Order.restaurant_id == DEFAULT_RESTAURANT_ID)\
        .filter(Order.status.in_(active_statuses))\
        .count()
    
    # Top items by popularity (most ordered)
    top_items_query = db.query(
        MenuItem.id,
        MenuItem.name,
        func.count(OrderItem.id).label('order_count'),
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(MenuItem.restaurant_id == DEFAULT_RESTAURANT_ID)\
     .group_by(MenuItem.id, MenuItem.name)\
     .order_by(func.count(OrderItem.id).desc())\
     .limit(5)\
     .all()
    
    # Total menu items count
    total_menu_items = db.query(MenuItem)\
        .filter(MenuItem.restaurant_id == DEFAULT_RESTAURANT_ID)\
        .count()
    
    return {
        "orders": orders_count,
        "revenue": revenue,
        "average_order": average_order,
        "active_orders": active_orders,
        "menu_items_count": total_menu_items,
        "top_items": [{
            "id": item.id,
            "name": item.name,
            "orders": item.order_count,
            "sold": item.total_sold
        } for item in top_items_query],
    }


@router.get("/orders-by-day")
def orders_by_day(db: Session = Depends(get_db)):
    """Get orders count for last 7 days."""
    from datetime import datetime, timedelta
    
    today = datetime.utcnow().date()
    data = []
    
    for i in range(6, -1, -1):  # Last 7 days (from 6 days ago to today)
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        count = db.query(Order)\
            .filter(Order.restaurant_id == DEFAULT_RESTAURANT_ID)\
            .filter(Order.created_at >= day_start)\
            .filter(Order.created_at <= day_end)\
            .count()
        
        data.append({
            "date": day.strftime("%d/%m"),
            "orders": count
        })
    
    return data
