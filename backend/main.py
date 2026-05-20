import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import Base, engine, SessionLocal
from backend.middleware import SecurityHeadersMiddleware, RateLimitMiddleware, AuditLogMiddleware

import backend.models  # noqa: F401  — register all models with Base

from backend.routers import (
    auth, users, categories, products, variants,
    reviews, cart, orders, payments, promocodes, analytics,
)

app = FastAPI(title="Men's Clothes API", version="2.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(AuditLogMiddleware)


# ── Routers ──────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(variants.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(promocodes.router)
app.include_router(analytics.router)


# ── Startup ──────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    _seed_default_users()
    _seed_catalog()
    _seed_test_orders()
    print("[OK] Backend startup complete — single service on port 8000")


def _seed_default_users():
    from backend.enums import UserRole
    from backend.security import hash_password
    from backend.models.user import User

    db = SessionLocal()
    try:
        defaults = [
            {"username": "admin", "password": "Admin1pass", "role": UserRole.SYSTEM_ADMIN, "name": "Адміністратор"},
            {"username": "manager", "password": "Manager1", "role": UserRole.MANAGER, "name": "Менеджер"},
            {"username": "client", "password": "Client1", "role": UserRole.CLIENT, "name": "Клієнт"},
        ]
        for ud in defaults:
            if not db.query(User).filter(User.username == ud["username"]).first():
                db.add(User(
                    username=ud["username"],
                    password=hash_password(ud["password"]),
                    role=ud["role"].value,
                    name=ud.get("name"),
                    is_verified=True,
                ))
                db.commit()
                print(f"[OK] User created: {ud['username']}")
    finally:
        db.close()


def _seed_catalog():
    import random
    from backend.models.category import Category
    from backend.models.product import MenuItem
    from backend.models.variant import ProductVariant

    db = SessionLocal()
    try:
        categories_data = ["Polo Shirts", "Sweaters", "Jackets, Coats & Vests", "Jeans & Denim"]
        cat_ids: dict[str, int] = {}
        for name in categories_data:
            existing = db.query(Category).filter(Category.name == name).first()
            if not existing:
                c = Category(name=name)
                db.add(c)
                db.commit()
                db.refresh(c)
                cat_ids[name] = c.id
            else:
                cat_ids[name] = existing.id

        items = [
            ("Polo Shirts", "Classic Polo Shirt White", "Timeless white polo shirt made from premium cotton blend. Perfect for casual and semi-formal occasions.", 159900, "https://images.unsplash.com/photo-1625910513413-5fc133c4e5a3?w=800&q=80"),
            ("Polo Shirts", "Classic Polo Shirt Navy", "Elegant navy blue polo shirt with three-button placket. Comfortable fit for everyday wear.", 159900, "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=800&q=80"),
            ("Polo Shirts", "Classic Polo Shirt Black", "Sophisticated black polo shirt with ribbed collar. Versatile piece for your wardrobe.", 159900, "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800&q=80"),
            ("Polo Shirts", "Classic Polo Shirt Gray", "Modern gray polo shirt with soft fabric. Ideal for business casual settings.", 159900, "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&q=80"),
            ("Polo Shirts", "Polo Shirt Red", "Bold red polo shirt with contrast stitching. Stand out with this vibrant color.", 169900, "https://images.unsplash.com/photo-1627225924765-552d49cf47ad?w=800&q=80"),
            ("Polo Shirts", "Polo Shirt Green", "Fresh green polo shirt with modern cut. Perfect for spring and summer.", 169900, "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&q=80"),
            ("Polo Shirts", "Polo Shirt Striped", "Classic striped polo shirt with horizontal lines. Sporty yet refined style.", 179900, "https://images.unsplash.com/photo-1589310243389-96a5483213a8?w=800&q=80"),
            ("Polo Shirts", "Performance Polo Shirt", "Athletic polo shirt with moisture-wicking fabric. Great for active lifestyle.", 199900, "https://images.unsplash.com/photo-1564859228273-274232fdb516?w=800&q=80"),
            ("Polo Shirts", "Long Sleeve Polo Shirt", "Long sleeve polo shirt for cooler weather. Maintains classic polo style with extra coverage.", 189900, "https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800&q=80"),
            ("Polo Shirts", "Polo Shirt Heather", "Heather gray polo shirt with textured fabric. Casual comfort meets style.", 169900, "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&q=80"),
            ("Sweaters", "Cable Knit Sweater", "Traditional cable knit sweater in classic patterns. Warm and cozy for winter.", 349900, "https://images.unsplash.com/photo-1638718235824-6cc5f1e2b29a?w=800&q=80"),
            ("Sweaters", "V-Neck Sweater Gray", "Sophisticated V-neck sweater in gray. Perfect layering piece for business casual.", 279900, "https://images.unsplash.com/photo-1614975059251-992f11792571?w=800&q=80"),
            ("Sweaters", "Turtleneck Sweater Black", "Elegant black turtleneck sweater. Timeless style for sophisticated look.", 299900, "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800&q=80"),
            ("Sweaters", "Crew Neck Sweater Navy", "Classic crew neck sweater in navy blue. Versatile and comfortable.", 269900, "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=800&q=80"),
            ("Sweaters", "Merino Wool Sweater", "Premium merino wool sweater. Natural fiber for exceptional warmth and comfort.", 449900, "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&q=80"),
            ("Sweaters", "Cardigan Sweater", "Button-front cardigan sweater. Layered style for cool weather.", 329900, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80"),
            ("Sweaters", "Pullover Sweater Beige", "Casual pullover sweater in beige. Soft and comfortable for everyday wear.", 289900, "https://images.unsplash.com/photo-1434389677669-e08b4cda3a6a?w=800&q=80"),
            ("Sweaters", "Cashmere Blend Sweater", "Luxurious cashmere blend sweater. Ultimate comfort and softness.", 549900, "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&q=80"),
            ("Sweaters", "Hooded Sweatshirt", "Casual hooded sweatshirt. Perfect for relaxed weekend style.", 249900, "https://images.unsplash.com/photo-1556821862-33ec0b91d01c?w=800&q=80"),
            ("Sweaters", "Zipper Sweater", "Modern zip-up sweater. Easy to wear and versatile styling option.", 299900, "https://images.unsplash.com/photo-1609873814058-a8928924184a?w=800&q=80"),
            ("Jackets, Coats & Vests", "Leather Jacket Black", "Classic black leather jacket. Timeless biker style with modern fit.", 899900, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80"),
            ("Jackets, Coats & Vests", "Denim Jacket Blue", "Classic blue denim jacket. Versatile piece for casual outfits.", 399900, "https://images.unsplash.com/photo-1576993537667-c6d2386f90a2?w=800&q=80"),
            ("Jackets, Coats & Vests", "Bomber Jacket", "Modern bomber jacket with ribbed cuffs. Sporty casual style.", 449900, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80"),
            ("Jackets, Coats & Vests", "Wool Coat Gray", "Elegant wool overcoat in gray. Sophisticated winter outerwear.", 1299900, "https://images.unsplash.com/photo-1544923246-77307dd270cb?w=800&q=80"),
            ("Jackets, Coats & Vests", "Trench Coat Beige", "Classic trench coat in beige. Timeless style for all occasions.", 999900, "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&q=80"),
            ("Jackets, Coats & Vests", "Puffer Jacket Black", "Warm puffer jacket in black. Lightweight yet insulating for cold weather.", 599900, "https://images.unsplash.com/photo-1548883354-94bcfe321cbb?w=800&q=80"),
            ("Jackets, Coats & Vests", "Blazer Navy", "Classic navy blazer. Essential for business casual and formal occasions.", 799900, "https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?w=800&q=80"),
            ("Jackets, Coats & Vests", "Quilted Vest", "Quilted vest for layering. Practical and stylish for transitional weather.", 349900, "https://images.unsplash.com/photo-1610652492500-ded49ceeb378?w=800&q=80"),
            ("Jackets, Coats & Vests", "Windbreaker Jacket", "Lightweight windbreaker jacket. Perfect for outdoor activities and travel.", 379900, "https://images.unsplash.com/photo-1545594861-3bef43ff2fc8?w=800&q=80"),
            ("Jackets, Coats & Vests", "Peacoat Navy", "Classic navy peacoat. Double-breasted design with warm wool construction.", 849900, "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80"),
            ("Jeans & Denim", "Classic Fit Jeans Blue", "Traditional classic fit jeans in blue denim. Comfortable straight leg design.", 329900, "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80"),
            ("Jeans & Denim", "Slim Fit Jeans Black", "Modern slim fit jeans in black. Contemporary cut for a streamlined look.", 349900, "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80"),
            ("Jeans & Denim", "Slim Fit Jeans Indigo", "Slim fit jeans in classic indigo blue. Versatile everyday denim.", 329900, "https://images.unsplash.com/photo-1604176354204-9268737828e4?w=800&q=80"),
            ("Jeans & Denim", "Straight Leg Jeans", "Straight leg jeans with regular rise. Traditional denim fit.", 319900, "https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=800&q=80"),
            ("Jeans & Denim", "Skinny Fit Jeans", "Skinny fit jeans for modern silhouette. Close-fitting throughout leg.", 359900, "https://images.unsplash.com/photo-1475178626620-a4d074967452?w=800&q=80"),
            ("Jeans & Denim", "Relaxed Fit Jeans", "Comfortable relaxed fit jeans. More room through seat and thigh.", 339900, "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?w=800&q=80"),
            ("Jeans & Denim", "Distressed Jeans", "Distressed jeans with vintage wash. Casual style with character.", 379900, "https://images.unsplash.com/photo-1565084888279-aca607ecce0c?w=800&q=80"),
            ("Jeans & Denim", "Dark Wash Jeans", "Dark wash jeans with deep indigo color. Dressier than light wash options.", 369900, "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&q=80"),
            ("Jeans & Denim", "Light Wash Jeans", "Light wash jeans with faded vintage look. Perfect for casual style.", 349900, "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=800&q=80"),
            ("Jeans & Denim", "Wide Leg Jeans", "Wide leg jeans with relaxed fit. Contemporary trend-forward style.", 389900, "https://images.unsplash.com/photo-1605518216938-7c31b7b14ad0?w=800&q=80"),
        ]

        sale_items = {
            "Classic Polo Shirt White": {"old_price": 199900, "badge": "sale"},
            "Polo Shirt Red": {"old_price": 219900, "badge": "sale"},
            "Performance Polo Shirt": {"old_price": None, "badge": "new"},
            "Cable Knit Sweater": {"old_price": 449900, "badge": "sale"},
            "Cashmere Blend Sweater": {"old_price": None, "badge": "new"},
            "Hooded Sweatshirt": {"old_price": 299900, "badge": "sale"},
            "Leather Jacket Black": {"old_price": 1099900, "badge": "sale"},
            "Bomber Jacket": {"old_price": None, "badge": "new"},
            "Classic Fit Jeans Blue": {"old_price": 399900, "badge": "sale"},
            "Distressed Jeans": {"old_price": None, "badge": "new"},
            "Wide Leg Jeans": {"old_price": None, "badge": "new"},
        }

        for cat_name, name, desc, price, img in items:
            cid = cat_ids.get(cat_name)
            if cid and not db.query(MenuItem).filter(MenuItem.name == name).first():
                extra = sale_items.get(name, {})
                db.add(MenuItem(
                    category_id=cid, name=name, description=desc, price=price, image_url=img,
                    old_price=extra.get("old_price"), badge=extra.get("badge"),
                ))
                db.commit()

        all_products = db.query(MenuItem).all()
        sizes = ["S", "M", "L", "XL"]
        variants_created = 0
        for p in all_products:
            if not db.query(ProductVariant).filter(ProductVariant.menu_item_id == p.id).first():
                for s in sizes:
                    db.add(ProductVariant(menu_item_id=p.id, size=s, stock=random.randint(10, 50)))
                    variants_created += 1
                db.commit()
        if variants_created:
            print(f"[OK] Created {variants_created} product variants")
    finally:
        db.close()


def _seed_test_orders():
    import random
    from datetime import timedelta
    from backend.models.order import Order, OrderItem
    from backend.models.product import MenuItem
    from backend.enums import OrderStatus, PaymentMethod

    db = SessionLocal()
    try:
        if db.query(Order).first():
            return

        prices: dict[int, int] = {}
        for p in db.query(MenuItem).all():
            prices[p.id] = p.price

        if not prices:
            return

        product_ids = list(prices.keys())
        test_user_ids = [1, 2, 3]
        addresses = [
            "вул. Хрещатик, 1, Київ", "просп. Перемоги, 42, Київ",
            "вул. Банкова, 5, Київ", "бул. Тараса Шевченка, 15, Київ",
            "вул. Саксаганського, 100, Київ",
        ]
        names = ["Олександр", "Андрій", "Максим", "Дмитро", "Іван"]
        surnames = ["Шевченко", "Бондаренко", "Коваленко", "Мельник", "Ткаченко"]
        phones = ["+380501234567", "+380671234567", "+380931234567", "+380661234567"]
        delivery_methods = ["nova_poshta", "ukrposhta", "self_pickup"]

        from datetime import datetime
        today = datetime.utcnow()
        count = 0
        for day_offset in range(29, -1, -1):
            order_date = today - timedelta(days=day_offset)
            n = random.randint(1, 4) if day_offset > 7 else random.randint(2, 6)
            for _ in range(n):
                h, m = random.randint(9, 22), random.randint(0, 59)
                dt = order_date.replace(hour=h, minute=m, second=0, microsecond=0)
                if day_offset < 3:
                    st = random.choice([OrderStatus.PENDING.value, OrderStatus.DELIVERING.value])
                elif day_offset < 14:
                    st = random.choice([OrderStatus.DELIVERING.value, OrderStatus.DELIVERED.value])
                else:
                    st = OrderStatus.DELIVERED.value

                selected = random.sample(product_ids, min(random.randint(1, 4), len(product_ids)))
                total = 0
                items_data = []
                for pid in selected:
                    qty = random.randint(1, 3)
                    p = prices[pid]
                    total += p * qty
                    items_data.append((pid, qty, p))

                order = Order(
                    user_id=random.choice(test_user_ids), status=st,
                    created_at=dt, updated_at=dt,
                    name=random.choice(names),
                    surname=random.choice(surnames),
                    phone=random.choice(phones),
                    email=f"user{random.randint(1,100)}@example.com",
                    delivery_address=random.choice(addresses),
                    delivery_method=random.choice(delivery_methods),
                    payment_method=PaymentMethod.CARD.value,
                    total_price=total,
                )
                db.add(order)
                db.flush()
                for pid, qty, p in items_data:
                    db.add(OrderItem(order_id=order.id, menu_item_id=pid, quantity=qty, price=p))
                count += 1
        db.commit()
        print(f"[OK] Created {count} test orders")
    finally:
        db.close()


# ── Health & Error handling ──────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "mens-clothes-api", "version": "2.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"ERROR: {request.method} {request.url} -> {type(exc).__name__}: {exc}")
    traceback.print_exc()
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
