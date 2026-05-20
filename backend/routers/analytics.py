from datetime import datetime, timedelta
from collections import defaultdict
from itertools import combinations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.order import Order, OrderItem
from backend.models.product import MenuItem
from backend.models.user import User
from backend.models.variant import ProductVariant
from backend.models.category import Category
from backend.models.payment import Payment
from backend.deps import require_roles
from backend.enums import UserRole, OrderStatus

router = APIRouter(prefix="/admin", tags=["admin:stats"])


def _resolve_period(days: int, start_date: Optional[str], end_date: Optional[str]):
    now = datetime.utcnow()
    if start_date and end_date:
        p_start = datetime.strptime(start_date, "%Y-%m-%d")
        p_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    else:
        p_end = now
        p_start = now - timedelta(days=days)
    return p_start, p_end


@router.get("/stats/orders-by-day")
def orders_by_day(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    data = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        count = db.query(Order).filter(Order.created_at >= day_start, Order.created_at <= day_end).count()
        data.append({"date": day.strftime("%d/%m"), "orders": count})
    return data


@router.get("/stats/products-by-period")
def products_by_period(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29)
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())

    orders_in_period = db.query(Order).filter(Order.created_at >= start_dt, Order.created_at <= end_dt).all()
    order_ids = [o.id for o in orders_in_period]
    if not order_ids:
        return []

    order_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all()
    products_by_date = defaultdict(lambda: defaultdict(int))
    for item in order_items:
        order = next((o for o in orders_in_period if o.id == item.order_id), None)
        if order:
            products_by_date[order.created_at.date()][item.menu_item_id] += item.quantity

    data = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_products = products_by_date.get(day, {})
        total_quantity = sum(day_products.values())
        product_details = []
        for mid, qty in sorted(day_products.items(), key=lambda x: x[1], reverse=True)[:5]:
            product = db.query(MenuItem).filter(MenuItem.id == mid).first()
            product_details.append({"id": mid, "name": product.name if product else "Unknown", "quantity": qty})
        data.append({"date": day.strftime("%d/%m"), "total_quantity": total_quantity, "unique_products": len(day_products), "top_products": product_details})
    return data


@router.get("/analytics/summary")
def analytics_summary(
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    ps, pe = _resolve_period(days, start_date, end_date)
    orders_count = db.query(func.count(Order.id)).filter(Order.created_at >= ps, Order.created_at < pe).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(Order.created_at >= ps, Order.created_at < pe).scalar()
    avg_order_value = db.query(func.coalesce(func.avg(Order.total_price), 0)).filter(Order.created_at >= ps, Order.created_at < pe).scalar()

    status_query = db.query(Order.status, func.count(Order.id).label("count")).filter(Order.created_at >= ps, Order.created_at < pe).group_by(Order.status).all()
    status_counts = {row.status: int(row.count) for row in status_query}
    orders_by_status = [{"status": s.value, "count": status_counts.get(s.value, 0)} for s in OrderStatus]

    new_customers = db.query(func.count(User.id)).filter(User.created_at >= ps, User.created_at < pe).scalar() or 0
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    new_customers_today = db.query(func.count(User.id)).filter(User.created_at >= today_start).scalar() or 0
    new_customers_week = db.query(func.count(User.id)).filter(User.created_at >= week_start).scalar() or 0

    top_products = (
        db.query(
            MenuItem.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue"),
        )
        .join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(MenuItem.id)
        .order_by(func.sum(OrderItem.quantity * OrderItem.price).desc())
        .limit(5)
        .all()
    )
    top_products_data = [
        {"name": p.name, "total_qty": int(p.total_qty), "total_revenue": int(p.total_revenue)}
        for p in top_products
    ]

    return {
        "total_orders": int(orders_count),
        "total_revenue": int(total_revenue),
        "avg_order_value": round(float(avg_order_value), 2),
        "new_customers": int(new_customers),
        "new_customers_today": int(new_customers_today),
        "new_customers_week": int(new_customers_week),
        "orders_by_status": orders_by_status,
        "top_products": top_products_data,
    }


@router.get("/analytics/top-products")
def analytics_top_products(
    days: int = 30,
    limit: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    ps, pe = _resolve_period(days, start_date, end_date)
    top_query = (
        db.query(
            OrderItem.menu_item_id,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(OrderItem.menu_item_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    results = []
    for row in top_query:
        product = db.query(MenuItem).filter(MenuItem.id == row.menu_item_id).first()
        results.append({
            "menu_item_id": row.menu_item_id,
            "name": product.name if product else f"Product #{row.menu_item_id}",
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
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    ps, pe = _resolve_period(days, start_date, end_date)

    if group_by == "day":
        rows = (
            db.query(
                func.date(Order.created_at).label("period"),
                func.coalesce(func.sum(Order.total_price), 0).label("revenue"),
                func.count(Order.id).label("orders"),
            )
            .filter(Order.created_at >= ps, Order.created_at < pe)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )
        return [{"period": str(r.period), "revenue": int(r.revenue), "orders": int(r.orders)} for r in rows]

    elif group_by == "week":
        orders_in_range = db.query(Order.created_at, Order.total_price).filter(Order.created_at >= ps, Order.created_at < pe).all()
        buckets: dict[str, dict] = defaultdict(lambda: {"revenue": 0, "orders": 0})
        for o in orders_in_range:
            iso = o.created_at.isocalendar()
            key = f"{iso[0]}-W{iso[1]:02d}"
            buckets[key]["revenue"] += o.total_price
            buckets[key]["orders"] += 1
        return [{"period": k, "revenue": int(v["revenue"]), "orders": v["orders"]} for k, v in sorted(buckets.items())]

    elif group_by == "month":
        orders_in_range = db.query(Order.created_at, Order.total_price).filter(Order.created_at >= ps, Order.created_at < pe).all()
        buckets: dict[str, dict] = defaultdict(lambda: {"revenue": 0, "orders": 0})
        for o in orders_in_range:
            key = o.created_at.strftime("%Y-%m")
            buckets[key]["revenue"] += o.total_price
            buckets[key]["orders"] += 1
        return [{"period": k, "revenue": int(v["revenue"]), "orders": v["orders"]} for k, v in sorted(buckets.items())]

    else:
        raise HTTPException(status_code=400, detail="group_by must be one of: day, week, month")


@router.get("/analytics/detailed")
def analytics_detailed(
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    ps, pe = _resolve_period(days, start_date, end_date)

    revenue_rows = (
        db.query(
            func.date(Order.created_at).label("d"),
            func.coalesce(func.sum(Order.total_price), 0).label("rev"),
            func.count(Order.id).label("cnt"),
        )
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    revenue_by_day = [{"date": str(r.d), "revenue": int(r.rev), "orders": int(r.cnt)} for r in revenue_rows]

    status_rows = (
        db.query(Order.status, func.count(Order.id))
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(Order.status)
        .all()
    )
    status_map = {s: c for s, c in status_rows}
    orders_by_status = [{"status": s.value, "count": status_map.get(s.value, 0)} for s in OrderStatus]

    now = datetime.utcnow()
    revenue_by_month = []
    for i in range(5, -1, -1):
        m_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        if i > 0:
            m_end = (m_start + timedelta(days=32)).replace(day=1)
        else:
            m_end = pe
        rev = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
            Order.created_at >= m_start, Order.created_at < m_end
        ).scalar()
        revenue_by_month.append({"month": m_start.strftime("%Y-%m"), "revenue": int(rev)})

    top_customers = (
        db.query(
            User.username, User.email,
            func.count(Order.id).label("orders_count"),
            func.coalesce(func.sum(Order.total_price), 0).label("total_spent"),
        )
        .join(Order, Order.user_id == User.id)
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(User.id)
        .order_by(func.sum(Order.total_price).desc())
        .limit(5)
        .all()
    )
    top_customers_data = [
        {"name": c.username, "email": c.email, "orders_count": int(c.orders_count), "total_spent": int(c.total_spent)}
        for c in top_customers
    ]

    pay_rows = (
        db.query(Order.payment_method, func.count(Order.id))
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(Order.payment_method)
        .all()
    )
    payment_methods = [{"method": m, "count": c} for m, c in pay_rows]

    del_rows = (
        db.query(Order.delivery_method, func.count(Order.id))
        .filter(Order.created_at >= ps, Order.created_at < pe)
        .group_by(Order.delivery_method)
        .all()
    )
    delivery_methods = [{"method": m or "unknown", "count": c} for m, c in del_rows]

    low_stock = (
        db.query(ProductVariant.size, ProductVariant.stock, MenuItem.name, Category.name.label("cat"))
        .join(MenuItem, MenuItem.id == ProductVariant.menu_item_id)
        .outerjoin(Category, Category.id == MenuItem.category_id)
        .filter(ProductVariant.stock < 10)
        .order_by(ProductVariant.stock)
        .limit(10)
        .all()
    )
    low_stock_data = [{"name": f"{r.name} ({r.size})", "stock": r.stock, "category": r.cat or "N/A"} for r in low_stock]

    prev_ps = ps - (pe - ps)
    prev_pe = ps
    prev_rev = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
        Order.created_at >= prev_ps, Order.created_at < prev_pe
    ).scalar()
    curr_rev = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
        Order.created_at >= ps, Order.created_at < pe
    ).scalar()
    prev_orders = db.query(func.count(Order.id)).filter(Order.created_at >= prev_ps, Order.created_at < prev_pe).scalar()
    curr_orders = db.query(func.count(Order.id)).filter(Order.created_at >= ps, Order.created_at < pe).scalar()
    prev_cust = db.query(func.count(distinct(User.id))).join(Order).filter(Order.created_at >= prev_ps, Order.created_at < prev_pe).scalar()
    curr_cust = db.query(func.count(distinct(User.id))).join(Order).filter(Order.created_at >= ps, Order.created_at < pe).scalar()

    def pct(curr, prev):
        return round((curr - prev) / prev * 100, 1) if prev else 0

    growth = {
        "revenue_change_percent": pct(curr_rev, prev_rev),
        "orders_change_percent": pct(curr_orders, prev_orders),
        "customers_change_percent": pct(curr_cust, prev_cust),
    }

    return {
        "revenue_by_day": revenue_by_day,
        "orders_by_status": orders_by_status,
        "revenue_by_month": revenue_by_month,
        "top_customers": top_customers_data,
        "payment_methods": payment_methods,
        "delivery_methods": delivery_methods,
        "low_stock_products": low_stock_data,
        "growth": growth,
    }


@router.get("/analytics/advanced")
def analytics_advanced(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN)),
):
    now = datetime.utcnow()

    # ── Customer segmentation ──
    cust_orders = (
        db.query(Order.user_id, func.count(Order.id).label("cnt"))
        .group_by(Order.user_id)
        .all()
    )
    buckets = {"1": 0, "2-5": 0, "5+": 0}
    for _, cnt in cust_orders:
        if cnt == 1:
            buckets["1"] += 1
        elif cnt <= 5:
            buckets["2-5"] += 1
        else:
            buckets["5+"] += 1
    customer_segmentation = [{"bucket": k, "count": v} for k, v in buckets.items()]

    # ── New vs returning this month ──
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_users = (
        db.query(Order.user_id)
        .filter(Order.created_at >= month_start)
        .distinct()
        .all()
    )
    month_user_ids = {u[0] for u in month_users}
    new_this_month = 0
    for uid in month_user_ids:
        first_order = db.query(func.min(Order.created_at)).filter(Order.user_id == uid).scalar()
        if first_order and first_order >= month_start:
            new_this_month += 1
    new_vs_returning = {
        "new_customers": new_this_month,
        "returning": len(month_user_ids) - new_this_month,
    }

    # ── CLV ──
    clv_data = (
        db.query(func.avg(
            db.query(func.sum(Order.total_price))
            .filter(Order.user_id == User.id)
            .correlate(User)
            .scalar_subquery()
        ))
        .select_from(User)
        .scalar()
    )
    customer_lifetime_value = round(float(clv_data or 0), 2)

    # ── Retention rate (31-60 days ago → ordered again in last 30 days) ──
    d30 = now - timedelta(days=30)
    d60 = now - timedelta(days=60)
    cohort = (
        db.query(distinct(Order.user_id))
        .filter(Order.created_at >= d60, Order.created_at < d30)
        .all()
    )
    cohort_ids = {r[0] for r in cohort}
    retained = 0
    if cohort_ids:
        retained = (
            db.query(func.count(distinct(Order.user_id)))
            .filter(Order.user_id.in_(cohort_ids), Order.created_at >= d30)
            .scalar() or 0
        )
    retention_rate = round(retained / len(cohort_ids) * 100, 1) if cohort_ids else 0

    # ── Orders by weekday / hour ──
    all_orders = db.query(Order.created_at, Order.total_price).all()
    weekday_stats = defaultdict(lambda: {"count": 0, "revenue": 0})
    hour_stats = defaultdict(lambda: {"count": 0, "revenue": 0})
    for o in all_orders:
        wd = o.created_at.weekday()
        weekday_stats[wd]["count"] += 1
        weekday_stats[wd]["revenue"] += o.total_price
        h = o.created_at.hour
        hour_stats[h]["count"] += 1
        hour_stats[h]["revenue"] += o.total_price

    orders_by_weekday = [{"day": d, "count": weekday_stats[d]["count"], "revenue": weekday_stats[d]["revenue"]} for d in range(7)]
    orders_by_hour = [{"hour": h, "count": hour_stats[h]["count"], "revenue": hour_stats[h]["revenue"]} for h in range(24)]

    # ── Status funnel & cancellation rate ──
    total_count = db.query(func.count(Order.id)).scalar() or 1
    cancelled_count = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.CANCELLED.value).scalar() or 0
    cancellation_rate = round(cancelled_count / total_count * 100, 1)

    status_funnel = []
    for s in OrderStatus:
        c = db.query(func.count(Order.id)).filter(Order.status == s.value).scalar()
        status_funnel.append({"status": s.value, "count": c})

    # ── Pending alerts ──
    d3 = now - timedelta(days=3)
    new_over_3d = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.PENDING.value, Order.created_at < d3
    ).scalar()
    delivering_over_3d = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.DELIVERING.value, Order.created_at < d3
    ).scalar()
    pending_orders = {"new_over_3d": new_over_3d, "processing_over_3d": delivering_over_3d}

    # ── Cross-sell pairs ──
    orders_with_items = (
        db.query(OrderItem.order_id, OrderItem.menu_item_id).all()
    )
    order_products = defaultdict(set)
    for oi in orders_with_items:
        order_products[oi.order_id].add(oi.menu_item_id)
    pair_counts = defaultdict(int)
    for products in order_products.values():
        if len(products) < 2:
            continue
        for a, b in combinations(sorted(products), 2):
            pair_counts[(a, b)] += 1
    top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    product_names = {}
    for (a, b), _ in top_pairs:
        for pid in (a, b):
            if pid not in product_names:
                p = db.query(MenuItem.name).filter(MenuItem.id == pid).first()
                product_names[pid] = p.name if p else f"#{pid}"
    cross_sell_pairs = [
        {"product_a": product_names[a], "product_b": product_names[b], "count": c}
        for (a, b), c in top_pairs
    ]

    # ── Never-sold products ──
    sold_ids = db.query(distinct(OrderItem.menu_item_id)).all()
    sold_set = {r[0] for r in sold_ids}
    never_sold_q = (
        db.query(MenuItem.name, Category.name.label("cat"))
        .outerjoin(Category, Category.id == MenuItem.category_id)
        .filter(~MenuItem.id.in_(sold_set) if sold_set else MenuItem.id.isnot(None))
        .limit(10)
        .all()
    )
    never_sold = [{"name": r.name, "category": r.cat or "N/A"} for r in never_sold_q]

    # ── Stock value ──
    stock_total = (
        db.query(func.coalesce(func.sum(ProductVariant.stock * MenuItem.price), 0))
        .join(MenuItem, MenuItem.id == ProductVariant.menu_item_id)
        .scalar()
    )

    # ── Sale impact (old_price means item is on sale) ──
    sale_items = db.query(MenuItem.id).filter(MenuItem.old_price.isnot(None)).all()
    sale_ids = {r[0] for r in sale_items}
    total_rev = db.query(func.coalesce(func.sum(OrderItem.quantity * OrderItem.price), 0)).scalar()
    if sale_ids:
        sale_rev = (
            db.query(func.coalesce(func.sum(OrderItem.quantity * OrderItem.price), 0))
            .filter(OrderItem.menu_item_id.in_(sale_ids))
            .scalar()
        )
        total_disc = (
            db.query(func.coalesce(func.sum(Order.discount), 0)).scalar()
        )
    else:
        sale_rev = 0
        total_disc = 0
    regular_rev = int(total_rev) - int(sale_rev)
    sale_impact = {
        "total_discount_given": int(total_disc),
        "sale_revenue_percent": round(int(sale_rev) / int(total_rev) * 100, 1) if total_rev else 0,
        "regular_revenue": regular_rev,
        "sale_revenue": int(sale_rev),
    }

    # ── AOV trend (30 days) ──
    aov_trend = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        ds = datetime.combine(day, datetime.min.time())
        de = datetime.combine(day, datetime.max.time())
        avg_val = db.query(func.avg(Order.total_price)).filter(
            Order.created_at >= ds, Order.created_at <= de
        ).scalar()
        aov_trend.append({"date": day.strftime("%Y-%m-%d"), "aov": round(float(avg_val or 0), 2)})

    # ── Revenue by payment method ──
    rev_by_pay = (
        db.query(
            Order.payment_method,
            func.sum(Order.total_price).label("rev"),
            func.count(Order.id).label("cnt"),
        )
        .group_by(Order.payment_method)
        .all()
    )
    revenue_by_payment_method = [
        {"method": r.payment_method, "revenue": int(r.rev), "count": int(r.cnt)}
        for r in rev_by_pay
    ]

    return {
        "customer_segmentation": customer_segmentation,
        "new_vs_returning": new_vs_returning,
        "customer_lifetime_value": customer_lifetime_value,
        "retention_rate": retention_rate,
        "orders_by_weekday": orders_by_weekday,
        "orders_by_hour": orders_by_hour,
        "status_funnel": status_funnel,
        "cancellation_rate": cancellation_rate,
        "pending_orders": pending_orders,
        "cross_sell_pairs": cross_sell_pairs,
        "never_sold_products": never_sold,
        "stock_value": int(stock_total),
        "sale_impact": sale_impact,
        "aov_trend": aov_trend,
        "revenue_by_payment_method": revenue_by_payment_method,
    }
