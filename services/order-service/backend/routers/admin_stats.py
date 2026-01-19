"""
Admin statistics endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.clients.catalog_client import get_catalog_client


router = APIRouter(prefix="/admin/stats", tags=["admin:stats"])


@router.get("/orders-by-day")
def orders_by_day(db: Session = Depends(get_db)):
    """Get orders count for last 30 days."""
    from datetime import datetime, timedelta
    
    today = datetime.utcnow().date()
    data = []
    days_range = 30
    
    for i in range(days_range - 1, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        count = db.query(Order)\
            .filter(Order.created_at >= day_start)\
            .filter(Order.created_at <= day_end)\
            .count()
        
        data.append({
            "date": day.strftime("%d/%m"),
            "orders": count
        })
    
    return data


@router.get("/products-by-period")
def products_by_period(db: Session = Depends(get_db)):
    """Get products sales statistics for last 30 days."""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    today = datetime.utcnow().date()
    
    # Last 30 days
    start_date = today - timedelta(days=29)
    days_range = 30
    
    # Get all orders in the period
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(today, datetime.max.time())
    
    orders_in_period = db.query(Order)\
        .filter(Order.created_at >= start_datetime)\
        .filter(Order.created_at <= end_datetime)\
        .all()
    
    order_ids = [o.id for o in orders_in_period]
    
    if not order_ids:
        return []
    
    # Get all order items for these orders
    order_items = db.query(OrderItem)\
        .filter(OrderItem.order_id.in_(order_ids))\
        .all()
    
    # Group order items by date and product ID
    products_by_date = defaultdict(lambda: defaultdict(int))
    
    for item in order_items:
        # Find the order to get creation date
        order = next((o for o in orders_in_period if o.id == item.order_id), None)
        if order:
            order_date = order.created_at.date()
            products_by_date[order_date][item.menu_item_id] += item.quantity
    
    # Build result data grouped by date
    catalog_client = get_catalog_client()
    data = []
    
    for i in range(days_range - 1, -1, -1):
        day = today - timedelta(days=i)
        day_products = products_by_date.get(day, {})
        
        # Count total products sold this day
        total_quantity = sum(day_products.values())
        
        # Get product details for top products of this day
        product_details = []
        for menu_item_id, quantity in sorted(day_products.items(), key=lambda x: x[1], reverse=True)[:5]:
            try:
                menu_item = catalog_client.get_product(menu_item_id)
                product_details.append({
                    "id": menu_item_id,
                    "name": menu_item.get("name", "Unknown"),
                    "quantity": quantity
                })
            except HTTPException:
                pass
        
        data.append({
            "date": day.strftime("%d/%m"),
            "total_quantity": total_quantity,
            "unique_products": len(day_products),
            "top_products": product_details
        })
    
    return data