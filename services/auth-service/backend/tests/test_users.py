"""
Tests for user management endpoints.
"""
import pytest


class TestGetUserById:
    """Tests for GET /users/{user_id} endpoint."""

    def test_get_user_by_id_success(self, client, test_user):
        """Test getting existing user by ID."""
        response = client.get(f"/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["role"] == test_user.role

    def test_get_user_by_id_not_found(self, client):
        """Test getting non-existent user by ID."""
        response = client.get("/users/99999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_user_by_id_invalid_id(self, client):
        """Test getting user with invalid ID format."""
        response = client.get("/users/invalid")
        assert response.status_code == 422


class TestGetUserByUsername:
    """Tests for GET /users/username/{username} endpoint."""

    def test_get_user_by_username_success(self, client, test_user):
        """Test getting existing user by username."""
        response = client.get(f"/users/username/{test_user.username}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["role"] == test_user.role

    def test_get_user_by_username_not_found(self, client):
        """Test getting non-existent user by username."""
        response = client.get("/users/username/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestGetCurrentUser:
    """Tests for GET /users/me endpoint."""

    def test_get_current_user_success(self, client, test_user, auth_headers):
        """Test getting current user with valid token."""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["role"] == test_user.role

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/users/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "authenticated" in data["detail"].lower()

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_get_current_user_expired_token(self, client):
        """Test getting current user with expired token."""
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


class TestUpdateMyProfile:
    """Tests for PUT /users/me endpoint."""

    def test_update_username_success(self, client, test_user, auth_headers, test_db):
        """Test updating username."""
        new_username = "newusername"
        response = client.put(
            "/users/me",
            headers=auth_headers,
            params={"username": new_username}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == new_username
        assert data["id"] == test_user.id

        # Verify in database
        test_db.refresh(test_user)
        assert test_user.username == new_username

    def test_update_password_success(self, client, test_user, auth_headers, test_db):
        """Test updating password."""
        new_password = "newpassword123"
        response = client.put(
            "/users/me",
            headers=auth_headers,
            params={"password": new_password}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id

        # Verify password was hashed and updated
        test_db.refresh(test_user)
        from backend.core.security import verify_password
        assert verify_password(new_password, test_user.password) is True

    def test_update_username_and_password(self, client, test_user, auth_headers, test_db):
        """Test updating both username and password."""
        new_username = "updateduser"
        new_password = "updatedpass123"
        response = client.put(
            "/users/me",
            headers=auth_headers,
            params={
                "username": new_username,
                "password": new_password
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == new_username

        # Verify both were updated
        test_db.refresh(test_user)
        assert test_user.username == new_username
        from backend.core.security import verify_password
        assert verify_password(new_password, test_user.password) is True

    def test_update_username_already_taken(self, client, test_user, auth_headers, test_db):
        """Test updating username to one that's already taken."""
        # Create another user
        from backend.models.user import User
        from backend.core.security import hash_password
        other_user = User(
            username="otheruser",
            password=hash_password("pass123"),
            role="client"
        )
        test_db.add(other_user)
        test_db.commit()

        # Try to update to taken username
        response = client.put(
            "/users/me",
            headers=auth_headers,
            params={"username": "otheruser"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "taken" in data["detail"].lower()

    def test_update_no_token(self, client):
        """Test updating profile without token."""
        response = client.put(
            "/users/me",
            params={"username": "newusername"}
        )
        assert response.status_code == 401

    def test_update_no_changes(self, client, test_user, auth_headers):
        """Test updating profile without any changes."""
        response = client.put(
            "/users/me",
            headers=auth_headers
        )
        # Should still return 200 as no validation errors
        assert response.status_code == 200
