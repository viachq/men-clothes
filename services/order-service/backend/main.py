"""
Order Service - Cart, Orders, Payments, and Statistics.
This service manages only Order, OrderItem, Payment, and Cart entities.
"""
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import Base
from backend.database.session import engine, SessionLocal

# Import only models managed by this service
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.payment import Payment
from backend.models.cart import Cart, CartItem
from backend.models.promo_code import PromoCode
from backend.core.enums import OrderStatus, PaymentMethod

# Import routers
from backend.routers import (
    cart,
    orders,
    admin_orders,
    payments,
    admin_stats,
    promocodes,
)

# Create FastAPI application
app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="Cart, Orders, Payments, and Statistics"
)


def init_db():
    """Initialize database tables for order-service (orders, order_items, payments, carts, cart_items)."""
    Base.metadata.create_all(bind=engine)
    print("[OK] Order service: Database tables created (orders, order_items, payments, carts, cart_items, promo_codes)")


def init_default_data():
    """Create test orders with order items for demonstration."""
    from datetime import datetime, timedelta
    import random
    from sqlalchemy.orm import Session
    
    db: Session = SessionLocal()
    try:
        # Check if orders already exist
        existing_orders = db.query(Order).first()
        if existing_orders:
            print("[OK] Test orders already exist, skipping initialization")
            return
        
        # Try to get menu items from catalog service for real prices
        menu_items_prices = {}
        try:
            from backend.clients.catalog_client import get_catalog_client
            catalog_client = get_catalog_client()
            # Try to fetch all menu items (limit to first 40)
            try:
                import httpx
                response = httpx.get(f"{catalog_client.base_url}/products/", timeout=5.0)
                if response.status_code == 200:
                    menu_items = response.json()
                    for item in menu_items[:40]:  # Limit to 40 items
                        menu_items_prices[item['id']] = item.get('price', 300000)
                    print(f"[OK] Fetched prices for {len(menu_items_prices)} menu items")
            except Exception:
                print("[WARN] Could not fetch menu items from catalog service, using estimated prices")
        except Exception:
            print("[WARN] Catalog service not available, using estimated prices")
        
        # Fallback prices by category ranges
        def get_item_price(menu_item_id: int) -> int:
            if menu_item_id in menu_items_prices:
                return menu_items_prices[menu_item_id]
            # Estimate prices: polo 1-10 (~159900), sweaters 11-20 (~349900), jackets 21-30 (~599900), jeans 31-40 (~329900)
            if 1 <= menu_item_id <= 10:
                return random.choice([159900, 169900, 179900, 189900, 199900])
            elif 11 <= menu_item_id <= 20:
                return random.choice([249900, 279900, 299900, 329900, 349900, 449900])
            elif 21 <= menu_item_id <= 30:
                return random.choice([399900, 449900, 599900, 799900, 899900, 999900])
            else:  # 31-40
                return random.choice([319900, 329900, 339900, 349900, 359900, 379900])
        
        # Test user IDs (assuming we have users with IDs 1-3)
        test_user_ids = [1, 2, 3]
        test_addresses = [
            "вул. Хрещатик, 1, Київ",
            "просп. Перемоги, 42, Київ",
            "вул. Банкова, 5, Київ",
            "бул. Тараса Шевченка, 15, Київ",
            "вул. Саксаганського, 100, Київ",
        ]
        
        # Product IDs (1-40 for 40 products we created)
        product_ids = list(range(1, 41))
        
        # Create orders for the last 30 days with some distribution
        today = datetime.utcnow()
        orders_created = 0
        
        for day_offset in range(29, -1, -1):
            order_date = today - timedelta(days=day_offset)
            
            # Create 1-4 orders per day (with more orders in recent days)
            orders_per_day = random.randint(1, 4) if day_offset > 7 else random.randint(2, 6)
            
            for _ in range(orders_per_day):
                # Random time during the day
                hour = random.randint(9, 22)
                minute = random.randint(0, 59)
                order_datetime = order_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Create order
                user_id = random.choice(test_user_ids)
                
                # Assign status based on date (older orders are more likely delivered)
                if day_offset < 3:
                    status = random.choice([OrderStatus.PENDING.value, OrderStatus.DELIVERING.value])
                elif day_offset < 14:
                    status = random.choice([OrderStatus.DELIVERING.value, OrderStatus.DELIVERED.value])
                else:
                    status = OrderStatus.DELIVERED.value
                
                # Select random products (1-4 items per order)
                num_items = random.randint(1, 4)
                selected_items = random.sample(product_ids, min(num_items, len(product_ids)))
                
                # Calculate total price with real or estimated prices
                total_price = 0
                order_items_data = []
                
                for product_id in selected_items:
                    quantity = random.randint(1, 3)
                    item_price = get_item_price(product_id)
                    total_price += item_price * quantity
                    order_items_data.append({
                        'menu_item_id': product_id,
                        'quantity': quantity,
                        'price': item_price
                    })
                
                order = Order(
                    user_id=user_id,
                    status=status,
                    created_at=order_datetime,
                    updated_at=order_datetime,
                    delivery_address=random.choice(test_addresses),
                    payment_method=PaymentMethod.CARD.value,
                    total_price=total_price,
                    delivery_time=order_datetime + timedelta(hours=random.randint(1, 3)) if status != OrderStatus.PENDING.value else None
                )
                db.add(order)
                db.flush()  # Get order ID
                
                # Create order items
                for item_data in order_items_data:
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=item_data['menu_item_id'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    db.add(order_item)
                
                orders_created += 1
        
        db.commit()
        print(f"[OK] Created {orders_created} test orders with order items")
    except Exception as e:
        print(f"[ERROR] Failed to create test orders: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


# CORS middleware - must be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()
    init_default_data()
    print("[OK] Order service: Startup complete")

# Include routers
# IMPORTANT: Admin routers must be registered BEFORE public routers
# to avoid path conflicts (e.g., /admin/orders/{id} vs /orders/{id})
app.include_router(admin_orders.router)
app.include_router(admin_stats.router)
app.include_router(promocodes.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)


# Health check endpoint
@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "order-service",
        "version": "1.0.0"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and log them."""
    print("=" * 60)
    print("ERROR OCCURRED:")
    print(f"Request: {request.method} {request.url}")
    print(f"Error: {type(exc).__name__}: {str(exc)}")
    print("\nTraceback:")
    traceback.print_exc()
    print("=" * 60)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc), "type": type(exc).__name__}
    )
