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
            ("Polo Shirts", "Classic Polo Shirt White", "Timeless white polo shirt made from premium cotton blend. Perfect for casual and semi-formal occasions.", 159900, "https://www.lorenzouomo.com/cdn/shop/products/Lu_Polo_ShortSleeve_WTMP02_IMAGE5_1200x.jpg?v=1650382170"),
            ("Polo Shirts", "Classic Polo Shirt Navy", "Elegant navy blue polo shirt with three-button placket. Comfortable fit for everyday wear.", 159900, "https://uselkfashions.com/cdn/shop/files/61cX_4S0URL._AC_SY741_large.jpg?v=1724585598"),
            ("Polo Shirts", "Classic Polo Shirt Black", "Sophisticated black polo shirt with ribbed collar. Versatile piece for your wardrobe.", 159900, "https://i5.walmartimages.com/asr/7bff3f9d-5686-469f-8162-6132f96ac48a.a9f55a1ad22c8d1d181f860b3decb1a9.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF"),
            ("Polo Shirts", "Classic Polo Shirt Gray", "Modern gray polo shirt with soft fabric. Ideal for business casual settings.", 159900, "https://collarsandco.com/cdn/shop/files/Collars-and-Co-TheAustin-White-with-Navy-Accent-Full_900x.jpg?v=1699982701"),
            ("Polo Shirts", "Polo Shirt Red", "Bold red polo shirt with contrast stitching. Stand out with this vibrant color.", 169900, "https://images.unsplash.com/photo-1503341504253-dff4815485f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"),
            ("Polo Shirts", "Polo Shirt Green", "Fresh green polo shirt with modern cut. Perfect for spring and summer.", 169900, "https://m.media-amazon.com/images/I/71HwjwGumiL._AC_UY1000_.jpg"),
            ("Polo Shirts", "Polo Shirt Striped", "Classic striped polo shirt with horizontal lines. Sporty yet refined style.", 179900, "https://extremelystoked.com/cdn/shop/files/mens-all-over-print-slim-fit-polo-shirt-white-left-front-66f2d5b4b90f2_1024x1024.jpg?v=1752523117"),
            ("Polo Shirts", "Performance Polo Shirt", "Athletic polo shirt with moisture-wicking fabric. Great for active lifestyle.", 199900, "https://sfycdn.speedsize.com/2780c694-3419-4266-9652-d242439affeb/stateandliberty.com/cdn/shop/products/felix3.jpg?v=1748369880&width=869"),
            ("Polo Shirts", "Long Sleeve Polo Shirt", "Long sleeve polo shirt for cooler weather. Maintains classic polo style with extra coverage.", 189900, "https://www.eight-x.com/cdn/shop/products/T-7007_White_04.jpg?v=1613672851"),
            ("Polo Shirts", "Polo Shirt Heather", "Heather gray polo shirt with textured fabric. Casual comfort meets style.", 169900, "https://images.unsplash.com/photo-1503341338985-b047bf74a116?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"),
            ("Sweaters", "Cable Knit Sweater", "Traditional cable knit sweater in classic patterns. Warm and cozy for winter.", 349900, "https://m.media-amazon.com/images/I/B1oPmlmoacL.jpg"),
            ("Sweaters", "V-Neck Sweater Gray", "Sophisticated V-neck sweater in gray. Perfect layering piece for business casual.", 279900, "https://lanamshop.com/cdn/shop/files/Mens_Camel_Hair_Cable_Knit_V-Neck_Sweater.jpg?v=1732391169&width=1946"),
            ("Sweaters", "Turtleneck Sweater Black", "Elegant black turtleneck sweater. Timeless style for sophisticated look.", 299900, "https://xrayjeans.com/cdn/shop/files/XMW-30019-ECRU-F3.webp?v=1764913825&width=2000"),
            ("Sweaters", "Crew Neck Sweater Navy", "Classic crew neck sweater in navy blue. Versatile and comfortable.", 269900, "https://www.jcrew.com/s7-img-facade/BA222_SU9811?hei=2000&crop=0,0,1600,0"),
            ("Sweaters", "Merino Wool Sweater", "Premium merino wool sweater. Natural fiber for exceptional warmth and comfort.", 449900, "https://www.jcrew.com/s7-img-facade/BS381_BR7024?$crop1254$"),
            ("Sweaters", "Cardigan Sweater", "Button-front cardigan sweater. Layered style for cool weather.", 329900, "https://www.westportbigandtall.com/cdn/shop/files/42683_GREY_1500x.jpg?v=1760706937"),
            ("Sweaters", "Pullover Sweater Beige", "Casual pullover sweater in beige. Soft and comfortable for everyday wear.", 289900, "https://m.media-amazon.com/images/I/81mVnv7JfoL._AC_UY1000_.jpg"),
            ("Sweaters", "Cashmere Blend Sweater", "Luxurious cashmere blend sweater. Ultimate comfort and softness.", 549900, "https://i.ebayimg.com/images/g/c~UAAOSwbvhmzirp/s-l400.jpg"),
            ("Sweaters", "Hooded Sweatshirt", "Casual hooded sweatshirt. Perfect for relaxed weekend style.", 249900, "https://m.media-amazon.com/images/I/81x21hBag3L._AC_UY350_.jpg"),
            ("Sweaters", "Zipper Sweater", "Modern zip-up sweater. Easy to wear and versatile styling option.", 299900, "https://m.media-amazon.com/images/I/51xLER6k9bL.jpg"),
            ("Jackets, Coats & Vests", "Leather Jacket Black", "Classic black leather jacket. Timeless biker style with modern fit.", 899900, "https://www.thejacketmaker.com/cdn/shop/files/Mens_Hooligan_Black_Leather_Trench_Coat_Made_of_100_Real_Cowhide_Leather_2b99d892-b277-4795-8986-58ba1ab32277.jpg?v=1756911425"),
            ("Jackets, Coats & Vests", "Denim Jacket Blue", "Classic blue denim jacket. Versatile piece for casual outfits.", 399900, "https://daruccinyc.com/cdn/shop/products/ISIMG-752660_1024x1024@2x.jpg?v=1678567688"),
            ("Jackets, Coats & Vests", "Bomber Jacket", "Modern bomber jacket with ribbed cuffs. Sporty casual style.", 449900, "https://jaminleather.com/wp-content/uploads/2024/08/MA241416GY_5925.jpg"),
            ("Jackets, Coats & Vests", "Wool Coat Gray", "Elegant wool overcoat in gray. Sophisticated winter outerwear.", 1299900, "https://i.insider.com/639cdb89b5600000185b2761?width=600&format=jpeg&auto=webp"),
            ("Jackets, Coats & Vests", "Trench Coat Beige", "Classic trench coat in beige. Timeless style for all occasions.", 999900, "https://cdn-ildmmeg.nitrocdn.com/HsBoHCElQfPSMjUNFwFaglHkPqsfelDP/assets/images/optimized/rev-04caedd/hespokestyle.com/wp-content/uploads/2014/10/hss-LEtrench-full-664x752.jpg"),
            ("Jackets, Coats & Vests", "Puffer Jacket Black", "Warm puffer jacket in black. Lightweight yet insulating for cold weather.", 599900, "https://m.media-amazon.com/images/I/71aMQ1bv97L._AC_UF894,1000_QL80_.jpg"),
            ("Jackets, Coats & Vests", "Blazer Navy", "Classic navy blazer. Essential for business casual and formal occasions.", 799900, "https://www.moviestarjacket.com/cdn/shop/files/Black-Leather-Blazer-for-Men.webp?v=1762168719&width=708"),
            ("Jackets, Coats & Vests", "Quilted Vest", "Quilted vest for layering. Practical and stylish for transitional weather.", 349900, "https://leatherkloset.com/cdn/shop/files/BMW3388_1800x.jpg?v=1707513897"),
            ("Jackets, Coats & Vests", "Windbreaker Jacket", "Lightweight windbreaker jacket. Perfect for outdoor activities and travel.", 379900, "https://jaminleather.com/wp-content/uploads/2024/08/MA2203D_9721.jpg"),
            ("Jackets, Coats & Vests", "Peacoat Navy", "Classic navy peacoat. Double-breasted design with warm wool construction.", 849900, "https://www.jcrew.com/s7-img-facade/BA222_SU9811?hei=2000&crop=0,0,1600,0"),
            ("Jeans & Denim", "Classic Fit Jeans Blue", "Traditional classic fit jeans in blue denim. Comfortable straight leg design.", 329900, "https://www.jlindeberg.com/cdn/shop/files/7c891fc32cbb226a3bbc9050c0c3f94b_001.jpg?v=1758719433&width=1200"),
            ("Jeans & Denim", "Slim Fit Jeans Black", "Modern slim fit jeans in black. Contemporary cut for a streamlined look.", 349900, "https://www.mishmashjeans.com/cdn/shop/files/mirage_blue_black_denim_jean_5000x_5f488b69-674c-4b9b-8c30-ad2096f9bfbb.png?v=1733405358"),
            ("Jeans & Denim", "Slim Fit Jeans Indigo", "Slim fit jeans in classic indigo blue. Versatile everyday denim.", 329900, "https://www.jlindeberg.com/cdn/shop/files/cf3dccd12c8cfdf74bdb4dbfa33dc15f_003.jpg?v=1758719433&width=1200"),
            ("Jeans & Denim", "Straight Leg Jeans", "Straight leg jeans with regular rise. Traditional denim fit.", 319900, "https://www.eight-x.com/cdn/shop/products/MG_1361_c4ed6e63-ca99-4250-9f4d-547deee868a4_460x@2x.jpg?v=1639761073"),
            ("Jeans & Denim", "Skinny Fit Jeans", "Skinny fit jeans for modern silhouette. Close-fitting throughout leg.", 359900, "https://turbobrandsfactory.com/cdn/shop/files/MDB-4_0d531f03-30b6-4fa9-977a-26d6c2b130a8.jpg?v=1733137599&width=1500"),
            ("Jeans & Denim", "Relaxed Fit Jeans", "Comfortable relaxed fit jeans. More room through seat and thigh.", 339900, "http://americantall.com/cdn/shop/files/American-Tall-Men-Dylan-Slim-Fit-Jeans-Faded-Blue-Black-front.jpg?v=1762199969"),
            ("Jeans & Denim", "Distressed Jeans", "Distressed jeans with vintage wash. Casual style with character.", 379900, "https://xcdn.next.co.uk/common/items/default/default/itemimages/3_4Ratio/product/lge/408050s2.jpg?im=Resize,width=750"),
            ("Jeans & Denim", "Dark Wash Jeans", "Dark wash jeans with deep indigo color. Dressier than light wash options.", 369900, "https://www.mishmashjeans.com/cdn/shop/files/mirage_blue_black_denim_jean_side_300x.jpg?v=1727261568"),
            ("Jeans & Denim", "Light Wash Jeans", "Light wash jeans with faded vintage look. Perfect for casual style.", 349900, "https://www.sportsdirect.com/images/imgzoom/64/64367918_xxl.jpg"),
            ("Jeans & Denim", "Wide Leg Jeans", "Wide leg jeans with relaxed fit. Contemporary trend-forward style.", 389900, "https://cdn.thewirecutter.com/wp-content/media/2024/12/FI-DEARBORN-JEANS-2048x1024px-2x1-1.png?width=2048&quality=75&crop=2:1&auto=webp"),
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
