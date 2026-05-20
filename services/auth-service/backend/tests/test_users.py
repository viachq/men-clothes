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
    """Tests for PUT /users/me endpoint (JSON body: name, email, phone, old_password, password)."""

    def test_update_name_success(self, client, test_user, auth_headers, test_db):
        """Test updating display name."""
        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={"name": "Новий Користувач"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новий Користувач"
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username  # username is immutable

        test_db.refresh(test_user)
        assert test_user.name == "Новий Користувач"

    def test_update_contact_info_success(self, client, test_user, auth_headers, test_db):
        """Test updating email and phone."""
        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={"email": "new@example.com", "phone": "+380501234567"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["phone"] == "+380501234567"

        test_db.refresh(test_user)
        assert test_user.email == "new@example.com"
        assert test_user.phone == "+380501234567"

    def test_update_password_success(self, client, test_user, auth_headers, test_db):
        """Test updating password (requires correct old_password)."""
        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={"old_password": "testpass123", "password": "newpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id

        test_db.refresh(test_user)
        from backend.core.security import verify_password
        assert verify_password("newpassword123", test_user.password) is True

    def test_update_password_wrong_old_password(self, client, test_user, auth_headers):
        """Test that changing password with a wrong old_password is rejected."""
        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={"old_password": "wrongold", "password": "newpassword123"}
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_update_email_already_taken(self, client, test_user, auth_headers, test_db):
        """Test updating email to one that's already registered to another user."""
        from backend.models.user import User
        from backend.core.security import hash_password
        other_user = User(
            username="otheruser",
            password=hash_password("pass123"),
            role="client",
            email="taken@example.com",
            is_verified=True,
        )
        test_db.add(other_user)
        test_db.commit()

        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={"email": "taken@example.com"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower()

    def test_update_no_token(self, client):
        """Test updating profile without token."""
        response = client.put(
            "/users/me",
            json={"name": "Anything"}
        )
        assert response.status_code == 401

    def test_update_no_changes(self, client, test_user, auth_headers):
        """Test updating profile with an empty body (no changes) returns 200."""
        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200
