"""
Tests for categories endpoints.
"""
import pytest


class TestListCategories:
    """Tests for GET /categories endpoint."""
    
    def test_list_categories_empty(self, client):
        """Test listing categories when none exist."""
        response = client.get("/categories/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_categories_with_data(self, client, test_category):
        """Test listing categories with data."""
        response = client.get("/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_category.id
        assert data[0]["name"] == test_category.name


class TestAdminCategories:
    """Tests for admin category endpoints."""
    
    def test_create_category_unauthorized(self, client):
        """Test creating category without authentication."""
        response = client.post("/admin/categories/", json={"name": "New Category"})
        assert response.status_code == 401
    
    def test_create_category_as_client(self, client, auth_headers):
        """Test creating category as regular client (should fail)."""
        response = client.post(
            "/admin/categories/",
            json={"name": "New Category"},
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_create_category_as_admin(self, client, admin_auth_headers, test_db):
        """Test creating category as admin."""
        response = client.post(
            "/admin/categories/",
            json={"name": "New Category"},
            headers=admin_auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"
        assert "id" in data
    
    def test_update_category_as_admin(self, client, admin_auth_headers, test_category):
        """Test updating category as admin."""
        response = client.put(
            f"/admin/categories/{test_category.id}",
            json={"name": "Updated Category"},
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category"
    
    def test_delete_category_as_admin(self, client, admin_auth_headers, test_category):
        """Test deleting category as admin."""
        response = client.delete(
            f"/admin/categories/{test_category.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == 204
        
        # Verify category is deleted
        get_response = client.get("/categories/")
        assert len(get_response.json()) == 0
