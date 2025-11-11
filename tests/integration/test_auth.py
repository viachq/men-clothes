"""
Integration tests for authentication endpoints.
Tests the full authentication flow: register → login → access protected endpoints.
"""
import pytest
from backend.core.enums import UserRole


class TestRegistration:
    """Tests for user registration."""
    
    def test_register_new_user_success(self, client):
        """Test successful registration of new user."""
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "password123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["username"] == "newuser"
        assert data["message"] == "User registered successfully"
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username."""
        response = client.post("/auth/register", json={
            "username": test_user.username,
            "password": "anypassword"
        })
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_empty_username(self, client):
        """Test registration with empty username."""
        response = client.post("/auth/register", json={
            "username": "",
            "password": "password123"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_register_empty_password(self, client):
        """Test registration with empty password."""
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": ""
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post("/auth/register", json={
            "username": "newuser"
            # Missing password
        })
        
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""
    
    def test_login_correct_credentials(self, client, test_user):
        """Test login with correct credentials."""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == test_user.id
        assert data["user"]["username"] == test_user.username
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent username."""
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "anypassword"
        })
        
        assert response.status_code == 401
    
    def test_login_empty_username(self, client):
        """Test login with empty username."""
        response = client.post("/auth/login", json={
            "username": "",
            "password": "password"
        })
        
        assert response.status_code in [401, 422]  # May be handled as invalid credentials or validation error
    
    def test_login_missing_password(self, client):
        """Test login without password."""
        response = client.post("/auth/login", json={
            "username": "testuser"
        })
        
        assert response.status_code == 422
    
    def test_login_returns_user_info(self, client, test_user):
        """Test that login returns complete user information."""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["id"] is not None
        assert data["user"]["username"] == "testuser"
        assert data["user"]["role"] == UserRole.CLIENT.value


class TestProtectedEndpoints:
    """Tests for access to protected endpoints."""
    
    def test_access_without_token(self, client):
        """Test that protected endpoint requires authentication."""
        response = client.get("/cart/me")
        assert response.status_code == 401
    
    def test_access_with_valid_token(self, client, auth_headers):
        """Test access to protected endpoint with valid token."""
        response = client.get("/cart/me", headers=auth_headers)
        assert response.status_code == 200
    
    def test_access_with_invalid_token(self, client):
        """Test access with invalid token."""
        response = client.get(
            "/cart/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_token_without_bearer_prefix(self, client, auth_headers):
        """Test token without 'Bearer' prefix."""
        token = auth_headers["Authorization"].replace("Bearer ", "")
        response = client.get(
            "/cart/me",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 401
    
    def test_admin_endpoint_requires_admin_role(self, client, auth_headers):
        """Test that admin endpoints require admin role."""
        response = client.get("/admin/orders", headers=auth_headers)
        assert response.status_code == 403  # Forbidden
    
    def test_admin_can_access_admin_endpoints(self, client, admin_headers):
        """Test that admin can access admin endpoints."""
        response = client.get("/admin/orders", headers=admin_headers)
        assert response.status_code == 200

