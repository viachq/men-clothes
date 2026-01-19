"""
Tests for dependency injection functions.
"""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.core.security import create_access_token, decode_token
from backend.models.user import User
from backend.core.enums import UserRole


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def test_get_current_user_valid_token(self, client, test_user):
        """Test getting current user with valid token."""
        token = create_access_token(test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username

    def test_get_current_user_no_token(self, client):
        """Test get_current_user without token raises 401."""
        response = client.get("/users/me")
        assert response.status_code == 401
        data = response.json()
        assert "authenticated" in data["detail"].lower()

    def test_get_current_user_invalid_token(self, client):
        """Test get_current_user with invalid token raises 401."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401

    def test_get_current_user_user_not_found(self, client, test_db):
        """Test get_current_user when user doesn't exist in DB."""
        # Create token for non-existent user
        token = create_access_token("nonexistentuser")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_current_user_expired_token(self, client):
        """Test get_current_user with expired token raises 401."""
        from datetime import datetime, timezone, timedelta
        from jose import jwt
        from backend.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

        # Create expired token
        expire = datetime.now(timezone.utc) - timedelta(minutes=1)
        to_encode = {
            "sub": "testuser",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        expired_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401

    def test_get_current_user_wrong_secret(self, client, test_user):
        """Test get_current_user with token signed with wrong secret."""
        from datetime import datetime, timezone, timedelta
        from jose import jwt

        # Create token with wrong secret
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        to_encode = {
            "sub": test_user.username,
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        wrong_token = jwt.encode(to_encode, "wrong-secret", algorithm="HS256")
        headers = {"Authorization": f"Bearer {wrong_token}"}

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401


class TestRequireRoles:
    """Tests for require_roles dependency."""

    def test_require_roles_system_admin_allowed(self, client, admin_user, admin_auth_headers):
        """Test that system admin can access admin endpoint."""
        response = client.get("/admin/users/", headers=admin_auth_headers)
        assert response.status_code == 200

    def test_require_roles_manager_allowed(self, client, manager_user, manager_auth_headers):
        """Test that manager can access admin endpoint."""
        response = client.get("/admin/users/", headers=manager_auth_headers)
        assert response.status_code == 200

    def test_require_roles_client_forbidden(self, client, test_user, auth_headers):
        """Test that client cannot access admin endpoint."""
        response = client.get("/admin/users/", headers=auth_headers)
        assert response.status_code == 403
        data = response.json()
        assert "forbidden" in data["detail"].lower()

    def test_require_roles_no_token(self, client):
        """Test require_roles without token raises 401."""
        response = client.get("/admin/users/")
        assert response.status_code == 401

    def test_require_roles_system_admin_only_endpoint(self, client, admin_user, admin_auth_headers, test_db):
        """Test endpoint that requires SYSTEM_ADMIN role only."""
        from backend.models.user import User
        from backend.core.security import hash_password

        # Create a test user to change role
        target_user = User(
            username="targetuser",
            password=hash_password("pass123"),
            role=UserRole.CLIENT.value
        )
        test_db.add(target_user)
        test_db.commit()

        # System admin can change role
        response = client.put(
            f"/admin/users/{target_user.id}/role",
            headers=admin_auth_headers,
            params={"role": "manager"}
        )
        assert response.status_code == 200

    def test_require_roles_manager_cannot_change_role(self, client, manager_user, manager_auth_headers, test_db):
        """Test that manager cannot change user role (SYSTEM_ADMIN only)."""
        from backend.models.user import User
        from backend.core.security import hash_password

        # Create a test user to change role
        target_user = User(
            username="targetuser2",
            password=hash_password("pass123"),
            role=UserRole.CLIENT.value
        )
        test_db.add(target_user)
        test_db.commit()

        # Manager cannot change role
        response = client.put(
            f"/admin/users/{target_user.id}/role",
            headers=manager_auth_headers,
            params={"role": "manager"}
        )
        assert response.status_code == 403
