"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database components
from backend.database import Base, get_db

# Import ALL models to register them with Base
from backend.models.user import User
from backend.models.menu_item import MenuItem
from backend.models.category import Category
from backend.models.cart import Cart, CartItem
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.restaurant import Restaurant
from backend.models.review import Review
from backend.models.payment import Payment

# Import routers
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

from backend.core.security import hash_password
from backend.core.enums import UserRole, OrderStatus
from backend.core.config import DEFAULT_RESTAURANT_ID


# Test database - in memory for each test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


def create_test_app() -> FastAPI:
    """Create a test FastAPI application without initialization logic."""
    test_app = FastAPI()
    
    # CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include all routers
    test_app.include_router(auth_register.router)
    test_app.include_router(auth_login.router)
    test_app.include_router(users_router.router)
    test_app.include_router(restaurants_router.router)
    test_app.include_router(admin_restaurants_router.router)
    test_app.include_router(categories_router.router)
    test_app.include_router(admin_categories_router.router)
    test_app.include_router(menu.router)
    test_app.include_router(admin_menu_router.router)
    test_app.include_router(cart_router.router)
    test_app.include_router(orders_router.router)
    test_app.include_router(admin_orders_router.router)
    test_app.include_router(payments_router.router)
    test_app.include_router(reviews_router.router)
    test_app.include_router(admin_stats_router.router)
    test_app.include_router(admin_users_router.router)
    
    return test_app


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine for each test."""
    # Create new in-memory database with StaticPool to share connection
    test_engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Important for in-memory SQLite!
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def test_db(db_engine):
    """Create a database session for each test."""
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestSession()
    
    # Create default restaurant
    restaurant = Restaurant(
        id=DEFAULT_RESTAURANT_ID,
        name="Test Restaurant",
        description="Test restaurant for testing",
        address="Test Address",
        phone="+380501234567",
        opening_hours="09:00-23:00"
    )
    db.add(restaurant)
    db.commit()
    
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_engine, test_db):
    """FastAPI test client with test database."""
    test_app = create_test_app()
    
    # Create a function that returns a new session from the same engine
    def override_get_db():
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        db = TestSession()
        try:
            yield db
        finally:
            db.close()
    
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as c:
        yield c
    test_app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test client user."""
    user = User(
        username="testuser",
        password=hash_password("testpass123"),
        role=UserRole.CLIENT.value
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_admin(test_db):
    """Create a test admin user."""
    admin = User(
        username="testadmin",
        password=hash_password("adminpass123"),
        role=UserRole.SYSTEM_ADMIN.value
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """Get authorization headers for test user."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Get authorization headers for admin user."""
    response = client.post("/auth/login", json={
        "username": "testadmin",
        "password": "adminpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category(test_db):
    """Create a test category."""
    category = Category(
        name="Test Category",
        description="Category for testing"
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def test_menu_item(test_db, test_category):
    """Create a test menu item."""
    item = MenuItem(
        restaurant_id=DEFAULT_RESTAURANT_ID,
        category_id=test_category.id,
        name="Test Pizza",
        description="Delicious test pizza",
        price=15000,  # 150 UAH
        image_url="https://example.com/pizza.jpg"
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item


@pytest.fixture
def test_menu_items(test_db, test_category):
    """Create multiple test menu items."""
    items = []
    for i in range(3):
        item = MenuItem(
            restaurant_id=DEFAULT_RESTAURANT_ID,
            category_id=test_category.id,
            name=f"Test Item {i+1}",
            description=f"Test description {i+1}",
            price=10000 + (i * 5000)
        )
        test_db.add(item)
        items.append(item)
    
    test_db.commit()
    for item in items:
        test_db.refresh(item)
    return items


@pytest.fixture
def test_cart(test_db, test_user):
    """Create a test cart."""
    cart = Cart(user_id=test_user.id)
    test_db.add(cart)
    test_db.commit()
    test_db.refresh(cart)
    return cart


@pytest.fixture
def test_cart_item(test_db, test_cart, test_menu_item):
    """Create a test cart item."""
    cart_item = CartItem(
        cart_id=test_cart.id,
        menu_item_id=test_menu_item.id,
        quantity=2,
        price=test_menu_item.price
    )
    test_db.add(cart_item)
    test_db.commit()
    test_db.refresh(cart_item)
    return cart_item

