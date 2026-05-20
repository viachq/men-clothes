"""
Admin statistics and analytics endpoints.
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.deps import require_roles
from backend.core.enums import UserRole, OrderStatus
from backend.clients.catalog_client import get_catalog_client


router = APIRouter(prefix="/admin", tags=["admin:stats"])


@router.get("/stats/orders-by-day")
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


@router.get("/stats/products-by-period")
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


# ── Enhanced Analytics Endpoints ──────────────────────────────────────

def _resolve_period(
    days: int,
    start_date: Optional[str],
    end_date: Optional[str],
) -> tuple[datetime, datetime]:
    """Resolve a time period from explicit dates or a rolling window."""
    now = datetime.utcnow()
    if start_date and end_date:
        p_start = datetime.strptime(start_date, "%Y-%m-%d")
        p_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    else:
        p_end = now
        p_start = now - timedelta(days=days)
    return p_start, p_end


@router.get("/analytics/summary")
def analytics_summary(
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    """
    Summary analytics: total orders, total revenue, average order value,
    and order counts grouped by status.
    """
    period_start, period_end = _resolve_period(days, start_date, end_date)

    # Total orders in the period
    orders_count = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= period_start, Order.created_at < period_end)
        .scalar()
    ) or 0

    # Total revenue in the period (in cents/kopiyky)
    total_revenue = (
        db.query(func.coalesce(func.sum(Order.total_price), 0))
        .filter(Order.created_at >= period_start, Order.created_at < period_end)
        .scalar()
    )

    # Average order value
    avg_order_value = (
        db.query(func.coalesce(func.avg(Order.total_price), 0))
        .filter(Order.created_at >= period_start, Order.created_at < period_end)
        .scalar()
    )

    # Orders grouped by status
    status_query = (
        db.query(Order.status, func.count(Order.id).label("count"))
        .filter(Order.created_at >= period_start, Order.created_at < period_end)
        .group_by(Order.status)
        .all()
    )
    status_counts = {row.status: int(row.count) for row in status_query}
    orders_by_status = [
        {"status": s.value, "count": status_counts.get(s.value, 0)}
        for s in OrderStatus
    ]

    return {
        "total_orders": int(orders_count),
        "total_revenue": int(total_revenue),
        "avg_order_value": round(float(avg_order_value), 2),
        "orders_by_status": orders_by_status,
    }


@router.get("/analytics/top-products")
def analytics_top_products(
    days: int = 30,
    limit: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    """
    Top selling products by total quantity sold within the period.
    Enriches results with product names from the catalog service when possible.
    """
    period_start, period_end = _resolve_period(days, start_date, end_date)

    top_query = (
        db.query(
            OrderItem.menu_item_id,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.created_at >= period_start, Order.created_at < period_end)
        .group_by(OrderItem.menu_item_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    catalog_client = get_catalog_client()
    results = []
    for row in top_query:
        product_name = f"Product #{row.menu_item_id}"
        try:
            product_info = catalog_client.get_product(row.menu_item_id)
            product_name = product_info.get("name", product_name)
        except Exception:
            pass

        results.append({
            "menu_item_id": row.menu_item_id,
            "name": product_name,
            "total_qty": int(row.total_qty),
            "total_revenue": int(row.total_revenue),
        })

    return results


@router.get("/analytics/revenue-by-period")
def analytics_revenue_by_period(
    days: int = 30,
    group_by: str = "day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    """
    Revenue grouped by day, week, or month.
    `group_by` accepts: "day", "week", "month".
    """
    period_start, period_end = _resolve_period(days, start_date, end_date)

    if group_by == "day":
        # Group by calendar date
        rows = (
            db.query(
                func.date(Order.created_at).label("period"),
                func.coalesce(func.sum(Order.total_price), 0).label("revenue"),
                func.count(Order.id).label("orders"),
            )
            .filter(Order.created_at >= period_start, Order.created_at < period_end)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )
        return [
            {
                "period": str(row.period),
                "revenue": int(row.revenue),
                "orders": int(row.orders),
            }
            for row in rows
        ]

    elif group_by == "week":
        # Build week buckets in Python for SQLite compatibility
        orders_in_range = (
            db.query(Order.created_at, Order.total_price)
            .filter(Order.created_at >= period_start, Order.created_at < period_end)
            .all()
        )
        week_buckets: dict[str, dict] = defaultdict(lambda: {"revenue": 0, "orders": 0})
        for o in orders_in_range:
            # ISO week start (Monday)
            iso_cal = o.created_at.isocalendar()
            week_label = f"{iso_cal[0]}-W{iso_cal[1]:02d}"
            week_buckets[week_label]["revenue"] += o.total_price
            week_buckets[week_label]["orders"] += 1

        return [
            {"period": k, "revenue": int(v["revenue"]), "orders": v["orders"]}
            for k, v in sorted(week_buckets.items())
        ]

    elif group_by == "month":
        # Build month buckets in Python for SQLite compatibility
        orders_in_range = (
            db.query(Order.created_at, Order.total_price)
            .filter(Order.created_at >= period_start, Order.created_at < period_end)
            .all()
        )
        month_buckets: dict[str, dict] = defaultdict(lambda: {"revenue": 0, "orders": 0})
        for o in orders_in_range:
            month_label = o.created_at.strftime("%Y-%m")
            month_buckets[month_label]["revenue"] += o.total_price
            month_buckets[month_label]["orders"] += 1

        return [
            {"period": k, "revenue": int(v["revenue"]), "orders": v["orders"]}
            for k, v in sorted(month_buckets.items())
        ]

    else:
        raise HTTPException(
            status_code=400,
            detail="group_by must be one of: day, week, month",
        )