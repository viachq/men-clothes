"""
Pytest configuration and fixtures for catalog-service tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch

from backend.database.base import Base
from backend.database.session import get_db
from backend.main import app
from backend.models.category import Category
from backend.models.menu_item import MenuItem
from backend.models.user import User
from backend.core.security import decode_token
from backend.core.enums import UserRole


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Create a test user object (mocked from auth-service)."""
    return User(
        id=1,
        username="testuser",
        role=UserRole.CLIENT.value
    )


@pytest.fixture
def admin_user():
    """Create an admin test user object (mocked from auth-service)."""
    return User(
        id=2,
        username="admin",
        role=UserRole.SYSTEM_ADMIN.value
    )


@pytest.fixture
def manager_user():
    """Create a manager test user object (mocked from auth-service)."""
    return User(
        id=3,
        username="manager",
        role=UserRole.MANAGER.value
    )


@pytest.fixture
def test_category(test_db):
    """Create a test category in the database."""
    category = Category(name="Test Category")
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def test_menu_item(test_db, test_category):
    """Create a test menu item in the database."""
    item = MenuItem(
        name="Test Product",
        description="Test Description",
        price=1000,  # 10.00 in cents
        category_id=test_category.id,
        image_url="https://example.com/image.jpg"
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    return item


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers with JWT token."""
    from backend.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": test_user.username, "exp": expire}
    token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user):
    """Create authorization headers with admin JWT token."""
    from backend.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": admin_user.username, "exp": expire}
    token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_auth_headers(manager_user):
    """Create authorization headers with manager JWT token."""
    from backend.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": manager_user.username, "exp": expire}
    token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_auth_client():
    """Mock auth client to avoid external HTTP calls."""
    with patch('backend.deps.get_auth_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        def get_user_by_username(username):
            users = {
                "testuser": {"id": 1, "username": "testuser", "role": "CLIENT"},
                "admin": {"id": 2, "username": "admin", "role": "SYSTEM_ADMIN"},
                "manager": {"id": 3, "username": "manager", "role": "MANAGER"},
            }
            if username in users:
                return users[username]
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="User not found")
        
        mock_client.get_user_by_username = get_user_by_username
        yield mock_client
