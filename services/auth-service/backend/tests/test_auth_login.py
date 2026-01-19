"""
Tests for user login endpoint.
"""
import pytest

from backend.core.security import verify_password


class TestLoginEndpoint:
    """Tests for POST /auth/login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login with correct credentials."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user.username,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == test_user.id
        assert data["user"]["username"] == test_user.username
        assert data["user"]["role"] == test_user.role
        assert len(data["access_token"]) > 0

    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_login_invalid_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_login_missing_username(self, client):
        """Test login without username."""
        response = client.post(
            "/auth/login",
            json={
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Test login without password."""
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser"
            }
        )
        assert response.status_code == 422

    def test_login_empty_json(self, client):
        """Test login with empty JSON."""
        response = client.post(
            "/auth/login",
            json={}
        )
        assert response.status_code == 422

    def test_login_token_is_valid(self, client, test_user):
        """Test that returned token is valid and can be decoded."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user.username,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        token = data["access_token"]

        # Verify token can be decoded
        from backend.core.security import decode_token
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == test_user.username

    def test_login_different_users_get_different_tokens(self, client, test_db):
        """Test that different users get different tokens."""
        from backend.models.user import User
        from backend.core.security import hash_password

        # Create two users
        user1 = User(
            username="user1",
            password=hash_password("pass1"),
            role="client"
        )
        user2 = User(
            username="user2",
            password=hash_password("pass2"),
            role="client"
        )
        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        # Login both users
        response1 = client.post(
            "/auth/login",
            json={"username": "user1", "password": "pass1"}
        )
        response2 = client.post(
            "/auth/login",
            json={"username": "user2", "password": "pass2"}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        assert token1 != token2
