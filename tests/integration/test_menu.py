"""
Integration tests for menu and category endpoints.
"""
import pytest


class TestPublicMenuAccess:
    """Tests for public (non-authenticated) menu access."""
    
    def test_get_all_menu_items(self, client, test_menu_items):
        """Test getting all menu items without authentication."""
        response = client.get("/menu/")
        
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        assert len(items) >= len(test_menu_items)
    
    def test_get_menu_item_by_id(self, client, test_menu_item):
        """Test getting specific menu item."""
        response = client.get(f"/menu/{test_menu_item.id}")
        
        assert response.status_code == 200
        item = response.json()
        assert item["id"] == test_menu_item.id
        assert item["name"] == test_menu_item.name
        assert item["price"] == test_menu_item.price
    
    def test_get_nonexistent_menu_item(self, client):
        """Test getting menu item that doesn't exist."""
        response = client.get("/menu/99999")
        
        assert response.status_code == 404
    
    def test_filter_menu_by_category(self, client, test_category, test_menu_item):
        """Test filtering menu items by category."""
        response = client.get(f"/menu/?category_id={test_category.id}")
        
        assert response.status_code == 200
        items = response.json()
        assert all(item["category_id"] == test_category.id for item in items)


class TestCategories:
    """Tests for category endpoints."""
    
    def test_get_all_categories(self, client, test_category):
        """Test getting all categories."""
        response = client.get("/categories/")
        
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
    
    def test_get_category_by_id(self, client, test_category):
        """Test getting specific category."""
        response = client.get(f"/categories/{test_category.id}")
        
        assert response.status_code == 200
        category = response.json()
        assert category["id"] == test_category.id
        assert category["name"] == test_category.name


class TestAdminMenuManagement:
    """Tests for admin menu management."""
    
    def test_create_menu_item_as_admin(self, client, admin_headers, test_category):
        """Test admin can create menu items."""
        response = client.post("/admin/menu", headers=admin_headers, json={
            "name": "New Pizza",
            "description": "Delicious new pizza",
            "price": 20000,
            "category_id": test_category.id,
            "image_url": "https://example.com/pizza.jpg"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
    
    def test_create_menu_item_as_client_forbidden(self, client, auth_headers):
        """Test client cannot create menu items."""
        response = client.post("/admin/menu", headers=auth_headers, json={
            "name": "Pizza",
            "description": "Test",
            "price": 10000
        })
        
        assert response.status_code == 403
    
    def test_update_menu_item_as_admin(self, client, admin_headers, test_menu_item):
        """Test admin can update menu items."""
        new_price = 25000
        response = client.put(
            f"/admin/menu/{test_menu_item.id}",
            headers=admin_headers,
            json={"price": new_price}
        )
        
        assert response.status_code == 200
        
        # Verify update
        item = client.get(f"/menu/{test_menu_item.id}").json()
        assert item["price"] == new_price
    
    def test_delete_menu_item_as_admin(self, client, admin_headers, test_menu_item):
        """Test admin can delete menu items."""
        response = client.delete(
            f"/admin/menu/{test_menu_item.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f"/menu/{test_menu_item.id}")
        assert get_response.status_code == 404
    
    def test_admin_can_create_category(self, client, admin_headers):
        """Test admin can create categories."""
        response = client.post("/admin/categories", headers=admin_headers, json={
            "name": "New Category",
            "description": "Test category"
        })
        
        assert response.status_code == 200
        assert "id" in response.json()
    
    def test_client_cannot_create_category(self, client, auth_headers):
        """Test client cannot create categories."""
        response = client.post("/admin/categories", headers=auth_headers, json={
            "name": "Category",
            "description": "Test"
        })
        
        assert response.status_code == 403

