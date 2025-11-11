"""
Main FastAPI application.
"""
import traceback
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import Base
from backend.database.session import engine

# Import models to ensure tables are registered
import backend.models  # noqa: F401

from backend.routers import (
    auth_register,
    auth_login,
    menu,
    users as users_router,
    restaurants as restaurants_router,
    admin_restaurants as admin_restaurants_router,
    categories as categories_router,
    admin_categories as admin_categories_router,
    admin_menu as admin_menu_router,
    cart as cart_router,
    orders as orders_router,
    admin_orders as admin_orders_router,
    payments as payments_router,
    reviews as reviews_router,
    admin_stats as admin_stats_router,
    admin_users as admin_users_router,
)

# Create FastAPI application
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize default data
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as SQLSession
from backend.models.restaurant import Restaurant
from backend.models.user import User
from backend.models.category import Category
from backend.models.menu_item import MenuItem
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.review import Review
from backend.core.config import DEFAULT_RESTAURANT_ID
from backend.core.enums import UserRole, OrderStatus, PaymentMethod
from backend.core.security import hash_password

db = SQLSession(bind=engine)
try:
    # Create default restaurant if doesn't exist
    if db.query(Restaurant).filter(Restaurant.id == DEFAULT_RESTAURANT_ID).first() is None:
        default_restaurant = Restaurant(
            id=DEFAULT_RESTAURANT_ID,
            name="Main Restaurant",
            description="Our main restaurant for food delivery",
            address="Kyiv, Ukraine",
            phone="+380501234567",
            opening_hours="09:00-23:00"
        )
        db.add(default_restaurant)
        db.commit()
        print(f"✓ Default restaurant created (ID: {DEFAULT_RESTAURANT_ID})")
    
    # Create default users if they don't exist
    default_users = [
        {
            "username": "admin",
            "password": "admin",
            "role": UserRole.SYSTEM_ADMIN,
            "display_name": "Системний адміністратор"
        },
        {
            "username": "restaurant_admin",
            "password": "restaurant_admin",
            "role": UserRole.RESTAURANT_ADMIN,
            "display_name": "Адміністратор ресторану"
        },
        {
            "username": "client",
            "password": "client",
            "role": UserRole.CLIENT,
            "display_name": "Тестовий клієнт"
        }
    ]
    
    created_users = {}
    for user_data in default_users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing is None:
            user = User(
                username=user_data["username"],
                password=hash_password(user_data["password"]),
                role=user_data["role"].value
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users[user_data["username"]] = user.id
            print(f"✓ User created: {user_data['username']} (password: {user_data['password']}, role: {user_data['role'].value})")
        else:
            created_users[user_data["username"]] = existing.id
    
    # Create default categories if they don't exist
    categories_data = [
        {
            "name": "Закуски та Салати",
            "description": "Почніть свій обід чи вечерю з ретельно підібраних інгредієнтів. Свіжі салати та вишукані холодні й гарячі закуски, що ідеально доповнять ваш вибір."
        },
        {
            "name": "Основні страви",
            "description": "Центральний елемент вашої трапези. Наші шеф-кухарі приготували добірні страви з м'яса, риби та птиці, а також класичні італійські пасти та різото."
        },
        {
            "name": "Десерти",
            "description": "Ідеальне завершення. Насолоджуйтесь нашою колекцією класичних десертів, свіжої випічки та фруктів, створених, щоб подарувати вам солодкі миті."
        }
    ]
    
    created_categories = {}
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if existing is None:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            created_categories[cat_data["name"]] = category.id
            print(f"✓ Category created: {cat_data['name']}")
        else:
            created_categories[cat_data["name"]] = existing.id
    
    # Create default menu items if they don't exist
    menu_items_data = [
        # Закуски та Салати
        {
            "category": "Закуски та Салати",
            "name": "Салат \"Цезар\" з куркою",
            "description": "Листя романо, хрусткі крутони, томати чері, пармезан та філе гриль під фірмовим соусом.",
            "price": 14500,  # 145 грн
            "image_url": "https://bandasmaku.com.ua/wp-content/uploads/2024/05/%D0%A6%D0%B5%D0%B7%D0%B0%D1%80-%D0%B7-%D0%BA%D1%83%D1%80%D0%BA%D0%BE%D1%8E-200-%D0%B3-140%E2%82%B4-600x400.webp"
        },
        {
            "category": "Закуски та Салати",
            "name": "Брускети з томатами та базиліком",
            "description": "Хрусткий багет з дрібно нарізаними томатами, часником, свіжим базиліком та оливковою олією.",
            "price": 12000,  # 120 грн
            "image_url": "https://eco-buffet.com/wp-content/uploads/2023/09/brusketa.png"
        },
        {
            "category": "Закуски та Салати",
            "name": "Сирна тарілка",
            "description": "Асорті з благородних сирів (брі, дорблю, пармезан) з медом, волоськими горіхами та виноградом.",
            "price": 18500,  # 185 грн
            "image_url": "https://unopizzagrill.com.ua/image/cache/catalog/menu/salad/7266-1920x1281.webp"
        },
        {
            "category": "Закуски та Салати",
            "name": "Карпачо з лосося",
            "description": "Тонкі скибочки свіжого лосося, заправлені лимонним соком, оливковою олією, з каперсами та руколою.",
            "price": 17000,  # 170 грн
            "image_url": "https://borges1896.com/app/uploads//14_62793819_%D0%9A%D0%90%D0%A0%D0%9F%D0%90%D0%A7%D0%A7%D0%9E-%D0%98%D0%97-%D0%9B%D0%9E%D0%A1%D0%9E%D0%A1%D0%AF.jpg"
        },
        # Основні страви
        {
            "category": "Основні страви",
            "name": "Стейк \"Нью-Йорк\" з овочами гриль",
            "description": "Соковитий стейк з яловичини, подається з обсмаженими на грилі болгарським перцем, кабачками та баклажанами.",
            "price": 35000,  # 350 грн
            "image_url": "https://assets.dots.live/misteram-public/018f42be-b319-7097-8858-817535fdd8dc-826x0.png"
        },
        {
            "category": "Основні страви",
            "name": "Паста Карбонара",
            "description": "Класична італійська паста зі спагеті, беконом, яєчним жовтком, сиром пекоріно та чорним перцем.",
            "price": 22000,  # 220 грн
            "image_url": "https://images.unian.net/photos/2021_03/thumb_files/1200_0_1615387932-9078.jpg"
        },
        {
            "category": "Основні страви",
            "name": "Філе дорадо з картопляним пюре",
            "description": "Ніжне філе морської риби, запечене з травами, подається з вершковим картопляним пюре та шпинатним соусом.",
            "price": 28000,  # 280 грн
            "image_url": "https://assets.dots.live/misteram-public/0186df23-805a-7177-b149-a5b238ffd0e7-826x0.png"
        },
        {
            "category": "Основні страви",
            "name": "Різото з білими грибами",
            "description": "Кремове різото з рисом арборіо, ароматними білими грибами, пармезаном та трюфельною олією.",
            "price": 24500,  # 245 грн
            "image_url": "https://assets.dots.live/misteram-public/0196a67f-eb11-70fb-8cdf-5ac3eac8e6ea-826x0.png"
        },
        # Десерти
        {
            "category": "Десерти",
            "name": "Шоколадний фондан",
            "description": "Гарячий шоколадний кекс з рідкою начинкою, подається з кулькою ванільного морозива.",
            "price": 11000,  # 110 грн
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQorpJnieWO0imrpB8qOX88Y6-8xl6dLbf-Uw&s"
        },
        {
            "category": "Десерти",
            "name": "Чізкейк \"Нью-Йорк\"",
            "description": "Класичний вершковий чізкейк на пісочній основі, подається зі свіжим ягідним соусом.",
            "price": 9500,   # 95 грн
            "image_url": "https://la-torta.ua/content/uploads/images/12-cake.jpg"
        },
        {
            "category": "Десерти",
            "name": "Тирамісу",
            "description": "Традиційний італійський десерт з печива савоярді, просоченого кавою, та ніжним кремом з маскарпоне.",
            "price": 10500,  # 105 грн
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKA5_dNLZhtefKQixJJTSLNI5fYOmPcdxScQ&s"
        },
        {
            "category": "Десерти",
            "name": "Фруктове асорті",
            "description": "Сезонні фрукти та ягоди (полуниця, лохина, ківі, апельсин), подаються з м'ятним сиропом.",
            "price": 8500,   # 85 грн
            "image_url": "https://retsepty.co.ua/wp-content/uploads/2025/04/Fruktove-asorti.jpg"
        }
    ]
    
    for item_data in menu_items_data:
        category_id = created_categories.get(item_data["category"])
        if category_id:
            existing = db.query(MenuItem).filter(
                MenuItem.name == item_data["name"],
                MenuItem.restaurant_id == DEFAULT_RESTAURANT_ID
            ).first()
            
            if existing is None:
                menu_item = MenuItem(
                    restaurant_id=DEFAULT_RESTAURANT_ID,
                    category_id=category_id,
                    name=item_data["name"],
                    description=item_data["description"],
                    price=item_data["price"],
                    image_url=item_data.get("image_url")
                )
                db.add(menu_item)
                db.commit()
                print(f"✓ Menu item created: {item_data['name']}")
    
    # Create default orders and reviews for the client user
    client_id = created_users.get("client")
    if client_id:
        # Check if we have menu items to create orders
        menu_items_list = db.query(MenuItem).filter(
            MenuItem.restaurant_id == DEFAULT_RESTAURANT_ID
        ).limit(5).all()
        
        if menu_items_list and db.query(Order).filter(Order.user_id == client_id).count() == 0:
            # Create 3 delivered orders with reviews
            reviews_data = [
                {
                    "rating": 5,
                    "text": "Чудова їжа! Все дуже смачно і свіжо. Доставили швидко, страви ще теплі. Салат Цезар просто неперевершений! Обов'язково замовлю ще.",
                    "days_ago": 5
                },
                {
                    "rating": 4,
                    "text": "Добрий сервіс та якісні продукти. Стейк приготований ідеально, а паста справжня італійська. Єдине зауваження - трохи довго доставляли, але загалом задоволений.",
                    "days_ago": 10
                },
                {
                    "rating": 5,
                    "text": "Десерти просто фантастичні! Тирамісу тає в роті, а чізкейк такий ніжний. Ціни адекватні, порції великі. Рекомендую всім!",
                    "days_ago": 15
                }
            ]
            
            for idx, review_data in enumerate(reviews_data):
                # Create order
                order_date = datetime.utcnow() - timedelta(days=review_data["days_ago"])
                order = Order(
                    user_id=client_id,
                    restaurant_id=DEFAULT_RESTAURANT_ID,
                    status=OrderStatus.DELIVERED.value,
                    delivery_address="вул. Хрещатик, 1, Київ",
                    payment_method=PaymentMethod.CARD.value,
                    total_price=sum(item.price for item in menu_items_list[:2]),
                    created_at=order_date,
                    updated_at=order_date,
                    delivery_time=order_date + timedelta(minutes=45)
                )
                db.add(order)
                db.commit()
                db.refresh(order)
                
                # Add order items
                for menu_item in menu_items_list[:2]:
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=menu_item.id,
                        quantity=1,
                        price=menu_item.price
                    )
                    db.add(order_item)
                db.commit()
                
                # Create review
                review = Review(
                    user_id=client_id,
                    order_id=order.id,
                    rating=review_data["rating"],
                    text=review_data["text"],
                    created_at=order_date + timedelta(hours=2)
                )
                db.add(review)
                db.commit()
                print(f"✓ Review created: {review_data['rating']}★ - {review_data['text'][:50]}...")
    
    print(f"✓ Database initialization complete!")
    
finally:
    db.close()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_register.router)
app.include_router(auth_login.router)
app.include_router(users_router.router)
app.include_router(restaurants_router.router)
app.include_router(admin_restaurants_router.router)
app.include_router(categories_router.router)
app.include_router(admin_categories_router.router)
app.include_router(menu.router)
app.include_router(admin_menu_router.router)
app.include_router(cart_router.router)
app.include_router(orders_router.router)
app.include_router(admin_orders_router.router)
app.include_router(payments_router.router)
app.include_router(reviews_router.router)
app.include_router(admin_stats_router.router)
app.include_router(admin_users_router.router)


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