"""
Pytest fixtures and configuration for auth-service tests.
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import backend
auth_service_path = Path(__file__).parent.parent
sys.path.insert(0, str(auth_service_path))

from backend.database.base import Base
from backend.database import get_db
from backend.main import app
from backend.models.user import User
from backend.core.security import hash_password, create_access_token
from backend.core.enums import UserRole


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def test_admin(test_db):
    """Create a test admin user in the database."""
    admin = User(
        username="adminuser",
        password=hash_password("adminpass123"),
        role=UserRole.SYSTEM_ADMIN.value
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def test_restaurant_admin(test_db):
    """Create a test restaurant admin user."""
    admin = User(
        username="restaurantadmin",
        password=hash_password("restpass123"),
        role=UserRole.RESTAURANT_ADMIN.value
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers for a test user."""
    token = create_access_token(test_user.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(test_admin):
    """Create authorization headers for an admin user."""
    token = create_access_token(test_admin.username)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def restaurant_admin_headers(test_restaurant_admin):
    """Create authorization headers for a restaurant admin."""
    token = create_access_token(test_restaurant_admin.username)
    return {"Authorization": f"Bearer {token}"}
