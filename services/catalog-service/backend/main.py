"""
Catalog Service - Store, Products, and Categories management.
This service manages Store, Category, and Product entities.
"""
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import Base
from backend.database.session import engine, SessionLocal

# Import only models managed by this service
from backend.models.category import Category
from backend.models.menu_item import MenuItem

# Import routers
from backend.routers import (
    categories,
    admin_categories,
    menu,
    admin_menu,
)

# Create FastAPI application
app = FastAPI(
    title="Catalog Service",
    version="1.0.0",
    description="Store, Products, and Categories management"
)


def init_db():
    """Initialize database tables for catalog-service (categories, products)."""
    Base.metadata.create_all(bind=engine)
    print("[OK] Catalog service: Database tables created (categories, menu_items)")


def init_default_data():
    """Create default categories and products if they don't exist."""
    db: Session = SessionLocal()
    try:
        # Create default categories if they don't exist
        categories_data = [
            {"name": "Polo Shirts"},
            {"name": "Sweaters"},
            {"name": "Jackets, Coats & Vests"},
            {"name": "Jeans & Denim"},
        ]

        created_categories = {}
        for cat_data in categories_data:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if existing is None:
                category = Category(
                    name=cat_data["name"]
                )
                db.add(category)
                db.commit()
                db.refresh(category)
                created_categories[cat_data["name"]] = category.id
                print(f"[OK] Category created: {cat_data['name']}")
            else:
                created_categories[cat_data["name"]] = existing.id

        # Create default products if they don't exist
        menu_items_data = [
            # Polo Shirts
            {"category": "Polo Shirts", "name": "Classic Polo Shirt White", "description": "Timeless white polo shirt made from premium cotton blend. Perfect for casual and semi-formal occasions.", "price": 159900, "image_url": "https://www.lorenzouomo.com/cdn/shop/products/Lu_Polo_ShortSleeve_WTMP02_IMAGE5_1200x.jpg?v=1650382170"},
            {"category": "Polo Shirts", "name": "Classic Polo Shirt Navy", "description": "Elegant navy blue polo shirt with three-button placket. Comfortable fit for everyday wear.", "price": 159900, "image_url": "https://uselkfashions.com/cdn/shop/files/61cX_4S0URL._AC_SY741_large.jpg?v=1724585598"},
            {"category": "Polo Shirts", "name": "Classic Polo Shirt Black", "description": "Sophisticated black polo shirt with ribbed collar. Versatile piece for your wardrobe.", "price": 159900, "image_url": "https://i5.walmartimages.com/asr/7bff3f9d-5686-469f-8162-6132f96ac48a.a9f55a1ad22c8d1d181f860b3decb1a9.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF"},
            {"category": "Polo Shirts", "name": "Classic Polo Shirt Gray", "description": "Modern gray polo shirt with soft fabric. Ideal for business casual settings.", "price": 159900, "image_url": "https://collarsandco.com/cdn/shop/files/Collars-and-Co-TheAustin-White-with-Navy-Accent-Full_900x.jpg?v=1699982701"},
            {"category": "Polo Shirts", "name": "Polo Shirt Red", "description": "Bold red polo shirt with contrast stitching. Stand out with this vibrant color.", "price": 169900, "image_url": "https://images.unsplash.com/photo-1503341504253-dff4815485f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
            {"category": "Polo Shirts", "name": "Polo Shirt Green", "description": "Fresh green polo shirt with modern cut. Perfect for spring and summer.", "price": 169900, "image_url": "https://m.media-amazon.com/images/I/71HwjwGumiL._AC_UY1000_.jpg"},
            {"category": "Polo Shirts", "name": "Polo Shirt Striped", "description": "Classic striped polo shirt with horizontal lines. Sporty yet refined style.", "price": 179900, "image_url": "https://extremelystoked.com/cdn/shop/files/mens-all-over-print-slim-fit-polo-shirt-white-left-front-66f2d5b4b90f2_1024x1024.jpg?v=1752523117"},
            {"category": "Polo Shirts", "name": "Performance Polo Shirt", "description": "Athletic polo shirt with moisture-wicking fabric. Great for active lifestyle.", "price": 199900, "image_url": "https://sfycdn.speedsize.com/2780c694-3419-4266-9652-d242439affeb/stateandliberty.com/cdn/shop/products/felix3.jpg?v=1748369880&width=869"},
            {"category": "Polo Shirts", "name": "Long Sleeve Polo Shirt", "description": "Long sleeve polo shirt for cooler weather. Maintains classic polo style with extra coverage.", "price": 189900, "image_url": "https://www.eight-x.com/cdn/shop/products/T-7007_White_04.jpg?v=1613672851"},
            {"category": "Polo Shirts", "name": "Polo Shirt Heather", "description": "Heather gray polo shirt with textured fabric. Casual comfort meets style.", "price": 169900, "image_url": "https://images.unsplash.com/photo-1503341338985-b047bf74a116?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
            # Sweaters
            {"category": "Sweaters", "name": "Cable Knit Sweater", "description": "Traditional cable knit sweater in classic patterns. Warm and cozy for winter.", "price": 349900, "image_url": "https://m.media-amazon.com/images/I/B1oPmlmoacL.jpg"},
            {"category": "Sweaters", "name": "V-Neck Sweater Gray", "description": "Sophisticated V-neck sweater in gray. Perfect layering piece for business casual.", "price": 279900, "image_url": "https://lanamshop.com/cdn/shop/files/Mens_Camel_Hair_Cable_Knit_V-Neck_Sweater.jpg?v=1732391169&width=1946"},
            {"category": "Sweaters", "name": "Turtleneck Sweater Black", "description": "Elegant black turtleneck sweater. Timeless style for sophisticated look.", "price": 299900, "image_url": "https://xrayjeans.com/cdn/shop/files/XMW-30019-ECRU-F3.webp?v=1764913825&width=2000"},
            {"category": "Sweaters", "name": "Crew Neck Sweater Navy", "description": "Classic crew neck sweater in navy blue. Versatile and comfortable.", "price": 269900, "image_url": "https://www.jcrew.com/s7-img-facade/BA222_SU9811?hei=2000&crop=0,0,1600,0"},
            {"category": "Sweaters", "name": "Merino Wool Sweater", "description": "Premium merino wool sweater. Natural fiber for exceptional warmth and comfort.", "price": 449900, "image_url": "https://www.jcrew.com/s7-img-facade/BS381_BR7024?$crop1254$"},
            {"category": "Sweaters", "name": "Cardigan Sweater", "description": "Button-front cardigan sweater. Layered style for cool weather.", "price": 329900, "image_url": "https://www.westportbigandtall.com/cdn/shop/files/42683_GREY_1500x.jpg?v=1760706937"},
            {"category": "Sweaters", "name": "Pullover Sweater Beige", "description": "Casual pullover sweater in beige. Soft and comfortable for everyday wear.", "price": 289900, "image_url": "https://m.media-amazon.com/images/I/81mVnv7JfoL._AC_UY1000_.jpg"},
            {"category": "Sweaters", "name": "Cashmere Blend Sweater", "description": "Luxurious cashmere blend sweater. Ultimate comfort and softness.", "price": 549900, "image_url": "https://i.ebayimg.com/images/g/c~UAAOSwbvhmzirp/s-l400.jpg"},
            {"category": "Sweaters", "name": "Hooded Sweatshirt", "description": "Casual hooded sweatshirt. Perfect for relaxed weekend style.", "price": 249900, "image_url": "https://m.media-amazon.com/images/I/81x21hBag3L._AC_UY350_.jpg"},
            {"category": "Sweaters", "name": "Zipper Sweater", "description": "Modern zip-up sweater. Easy to wear and versatile styling option.", "price": 299900, "image_url": "https://m.media-amazon.com/images/I/51xLER6k9bL.jpg"},
            # Jackets, Coats & Vests
            {"category": "Jackets, Coats & Vests", "name": "Leather Jacket Black", "description": "Classic black leather jacket. Timeless biker style with modern fit.", "price": 899900, "image_url": "https://www.thejacketmaker.com/cdn/shop/files/Mens_Hooligan_Black_Leather_Trench_Coat_Made_of_100_Real_Cowhide_Leather_2b99d892-b277-4795-8986-58ba1ab32277.jpg?v=1756911425"},
            {"category": "Jackets, Coats & Vests", "name": "Denim Jacket Blue", "description": "Classic blue denim jacket. Versatile piece for casual outfits.", "price": 399900, "image_url": "https://daruccinyc.com/cdn/shop/products/ISIMG-752660_1024x1024@2x.jpg?v=1678567688"},
            {"category": "Jackets, Coats & Vests", "name": "Bomber Jacket", "description": "Modern bomber jacket with ribbed cuffs. Sporty casual style.", "price": 449900, "image_url": "https://jaminleather.com/wp-content/uploads/2024/08/MA241416GY_5925.jpg"},
            {"category": "Jackets, Coats & Vests", "name": "Wool Coat Gray", "description": "Elegant wool overcoat in gray. Sophisticated winter outerwear.", "price": 1299900, "image_url": "https://i.insider.com/639cdb89b5600000185b2761?width=600&format=jpeg&auto=webp"},
            {"category": "Jackets, Coats & Vests", "name": "Trench Coat Beige", "description": "Classic trench coat in beige. Timeless style for all occasions.", "price": 999900, "image_url": "https://cdn-ildmmeg.nitrocdn.com/HsBoHCElQfPSMjUNFwFaglHkPqsfelDP/assets/images/optimized/rev-04caedd/hespokestyle.com/wp-content/uploads/2014/10/hss-LEtrench-full-664x752.jpg"},
            {"category": "Jackets, Coats & Vests", "name": "Puffer Jacket Black", "description": "Warm puffer jacket in black. Lightweight yet insulating for cold weather.", "price": 599900, "image_url": "https://m.media-amazon.com/images/I/71aMQ1bv97L._AC_UF894,1000_QL80_.jpg"},
            {"category": "Jackets, Coats & Vests", "name": "Blazer Navy", "description": "Classic navy blazer. Essential for business casual and formal occasions.", "price": 799900, "image_url": "https://www.moviestarjacket.com/cdn/shop/files/Black-Leather-Blazer-for-Men.webp?v=1762168719&width=708"},
            {"category": "Jackets, Coats & Vests", "name": "Quilted Vest", "description": "Quilted vest for layering. Practical and stylish for transitional weather.", "price": 349900, "image_url": "https://leatherkloset.com/cdn/shop/files/BMW3388_1800x.jpg?v=1707513897"},
            {"category": "Jackets, Coats & Vests", "name": "Windbreaker Jacket", "description": "Lightweight windbreaker jacket. Perfect for outdoor activities and travel.", "price": 379900, "image_url": "https://jaminleather.com/wp-content/uploads/2024/08/MA2203D_9721.jpg"},
            {"category": "Jackets, Coats & Vests", "name": "Peacoat Navy", "description": "Classic navy peacoat. Double-breasted design with warm wool construction.", "price": 849900, "image_url": "https://www.jcrew.com/s7-img-facade/BA222_SU9811?hei=2000&crop=0,0,1600,0"},
            # Jeans & Denim
            {"category": "Jeans & Denim", "name": "Classic Fit Jeans Blue", "description": "Traditional classic fit jeans in blue denim. Comfortable straight leg design.", "price": 329900, "image_url": "https://www.jlindeberg.com/cdn/shop/files/7c891fc32cbb226a3bbc9050c0c3f94b_001.jpg?v=1758719433&width=1200"},
            {"category": "Jeans & Denim", "name": "Slim Fit Jeans Black", "description": "Modern slim fit jeans in black. Contemporary cut for a streamlined look.", "price": 349900, "image_url": "https://www.mishmashjeans.com/cdn/shop/files/mirage_blue_black_denim_jean_5000x_5f488b69-674c-4b9b-8c30-ad2096f9bfbb.png?v=1733405358"},
            {"category": "Jeans & Denim", "name": "Slim Fit Jeans Indigo", "description": "Slim fit jeans in classic indigo blue. Versatile everyday denim.", "price": 329900, "image_url": "https://www.jlindeberg.com/cdn/shop/files/cf3dccd12c8cfdf74bdb4dbfa33dc15f_003.jpg?v=1758719433&width=1200"},
            {"category": "Jeans & Denim", "name": "Straight Leg Jeans", "description": "Straight leg jeans with regular rise. Traditional denim fit.", "price": 319900, "image_url": "https://www.eight-x.com/cdn/shop/products/MG_1361_c4ed6e63-ca99-4250-9f4d-547deee868a4_460x@2x.jpg?v=1639761073"},
            {"category": "Jeans & Denim", "name": "Skinny Fit Jeans", "description": "Skinny fit jeans for modern silhouette. Close-fitting throughout leg.", "price": 359900, "image_url": "https://turbobrandsfactory.com/cdn/shop/files/MDB-4_0d531f03-30b6-4fa9-977a-26d6c2b130a8.jpg?v=1733137599&width=1500"},
            {"category": "Jeans & Denim", "name": "Relaxed Fit Jeans", "description": "Comfortable relaxed fit jeans. More room through seat and thigh.", "price": 339900, "image_url": "http://americantall.com/cdn/shop/files/American-Tall-Men-Dylan-Slim-Fit-Jeans-Faded-Blue-Black-front.jpg?v=1762199969"},
            {"category": "Jeans & Denim", "name": "Distressed Jeans", "description": "Distressed jeans with vintage wash. Casual style with character.", "price": 379900, "image_url": "https://xcdn.next.co.uk/common/items/default/default/itemimages/3_4Ratio/product/lge/408050s2.jpg?im=Resize,width=750"},
            {"category": "Jeans & Denim", "name": "Dark Wash Jeans", "description": "Dark wash jeans with deep indigo color. Dressier than light wash options.", "price": 369900, "image_url": "https://www.mishmashjeans.com/cdn/shop/files/mirage_blue_black_denim_jean_side_300x.jpg?v=1727261568"},
            {"category": "Jeans & Denim", "name": "Light Wash Jeans", "description": "Light wash jeans with faded vintage look. Perfect for casual style.", "price": 349900, "image_url": "https://www.sportsdirect.com/images/imgzoom/64/64367918_xxl.jpg"},
            {"category": "Jeans & Denim", "name": "Wide Leg Jeans", "description": "Wide leg jeans with relaxed fit. Contemporary trend-forward style.", "price": 389900, "image_url": "https://cdn.thewirecutter.com/wp-content/media/2024/12/FI-DEARBORN-JEANS-2048x1024px-2x1-1.png?width=2048&quality=75&crop=2:1&auto=webp"}
        ]

        for item_data in menu_items_data:
            category_id = created_categories.get(item_data["category"])
            if category_id:
                existing = db.query(MenuItem).filter(
                    MenuItem.name == item_data["name"]
                ).first()

                if existing is None:
                    menu_item = MenuItem(
                        category_id=category_id,
                        name=item_data["name"],
                        description=item_data["description"],
                        price=item_data["price"],
                        image_url=item_data.get("image_url")
                    )
                    db.add(menu_item)
                    db.commit()
                    print(f"[OK] Product created: {item_data['name']}")
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
    print("[OK] Catalog service: Startup complete")

# Include routers
# IMPORTANT: Admin routers must be registered BEFORE public routers
# to avoid path conflicts (e.g., /admin/products/{id} vs /products/{id})
app.include_router(admin_categories.router)
app.include_router(admin_menu.router)
app.include_router(categories.router)
app.include_router(menu.router)


# Health check endpoint
@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "catalog-service",
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
