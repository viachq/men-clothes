"""
Tests for user registration endpoint.
"""
import pytest

from backend.models.user import User
from backend.core.enums import UserRole


class TestRegisterEndpoint:
    """Tests for POST /auth/register endpoint."""

    def test_register_success(self, client, test_db):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "verification_token" in data
        assert "user" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["is_verified"] is False

        # Verify user was created in database, unverified, with a token
        user = test_db.query(User).filter(User.username == "newuser").first()
        assert user is not None
        assert user.role == UserRole.CLIENT.value
        assert user.is_verified is False
        assert user.verification_token is not None

    def test_register_username_already_exists(self, client, test_user):
        """Test registration with existing username."""
        response = client.post(
            "/auth/register",
            json={
                "username": test_user.username,
                "password": "password123"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "зайня" in data["detail"].lower()

    def test_register_username_too_short(self, client):
        """Test registration with username too short."""
        response = client.post(
            "/auth/register",
            json={
                "username": "ab",  # min_length is 3
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_username_too_long(self, client):
        """Test registration with username too long."""
        response = client.post(
            "/auth/register",
            json={
                "username": "a" * 51,  # max_length is 50
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_password_too_short(self, client):
        """Test registration with password too short."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "password": "12345"  # min_length is 6
            }
        )
        assert response.status_code == 422

    def test_register_password_too_long(self, client):
        """Test registration with password too long."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "password": "a" * 73  # max_length is 72
            }
        )
        assert response.status_code == 422

    def test_register_password_is_hashed(self, client, test_db):
        """Test that password is hashed when stored."""
        password = "plainpassword123"
        response = client.post(
            "/auth/register",
            json={
                "username": "hasheduser",
                "password": password
            }
        )
        assert response.status_code == 201

        # Verify password is hashed in database
        user = test_db.query(User).filter(User.username == "hasheduser").first()
        assert user is not None
        assert user.password != password
        assert '$' in user.password  # Should contain salt$hash format

    def test_register_default_role_is_client(self, client, test_db):
        """Test that new user has CLIENT role by default."""
        response = client.post(
            "/auth/register",
            json={
                "username": "clientuser",
                "password": "password123"
            }
        )
        assert response.status_code == 201

        user = test_db.query(User).filter(User.username == "clientuser").first()
        assert user.role == UserRole.CLIENT.value

    def test_register_missing_username(self, client):
        """Test registration without username."""
        response = client.post(
            "/auth/register",
            json={
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_missing_password(self, client):
        """Test registration without password."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser"
            }
        )
        assert response.status_code == 422

    def test_register_empty_json(self, client):
        """Test registration with empty JSON."""
        response = client.post(
            "/auth/register",
            json={}
        )
        assert response.status_code == 422
