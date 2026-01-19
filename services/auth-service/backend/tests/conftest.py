"""
Pytest configuration and fixtures for auth-service tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.base import Base
from backend.database.session import get_db
from backend.main import app
from backend.models.user import User
from backend.core.security import hash_password, create_access_token
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
def test_user(test_db):
    """Create a test user in the database."""
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
def admin_user(test_db):
    """Create an admin test user in the database."""
    user = User(
        username="admin",
        password=hash_password("admin123"),
        role=UserRole.SYSTEM_ADMIN.value
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def manager_user(test_db):
    """Create a manager test user in the database."""
    user = User(
        username="manager",
        password=hash_password("manager123"),
        role=UserRole.MANAGER.value
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers with JWT token."""
    token = create_access_token(test_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user):
    """Create authorization headers with admin JWT token."""
    token = create_access_token(admin_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_auth_headers(manager_user):
    """Create authorization headers with manager JWT token."""
    token = create_access_token(manager_user.username)
    return {"Authorization": f"Bearer {token}"}
