"""
Tests for menu/products endpoints.
"""
import pytest


class TestListProducts:
    """Tests for GET /products endpoint."""
    
    def test_list_products_empty(self, client):
        """Test listing products when none exist."""
        response = client.get("/products/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_products_with_data(self, client, test_menu_item, test_db):
        """Test listing products with data."""
        # Force refresh the cache
        test_db.refresh(test_menu_item)
        # Clear cache to force fresh query
        from backend.routers.menu import clear_products_cache
        clear_products_cache()
        
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_menu_item.id
        assert data[0]["name"] == test_menu_item.name
        assert data[0]["price"] == test_menu_item.price
    
    def test_list_products_filter_by_category(self, client, test_category, test_menu_item, test_db):
        """Test filtering products by category."""
        from backend.models.category import Category
        from backend.models.menu_item import MenuItem
        
        # Create another category and product
        category2 = Category(name="Category 2")
        test_db.add(category2)
        test_db.commit()
        test_db.refresh(category2)
        
        item2 = MenuItem(
            name="Product 2",
            price=2000,
            category_id=category2.id
        )
        test_db.add(item2)
        test_db.commit()
        
        # Filter by category
        response = client.get(f"/products/?category_id={test_category.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category_id"] == test_category.id
    
    def test_list_products_search(self, client, test_menu_item, test_db):
        """Test searching products by name."""
        from backend.models.menu_item import MenuItem
        
        # Create another product
        item2 = MenuItem(
            name="Another Product",
            price=2000
        )
        test_db.add(item2)
        test_db.commit()
        
        # Search
        response = client.get("/products/?q=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Test" in data[0]["name"]


class TestAdminMenu:
    """Tests for admin menu endpoints."""
    
    def test_create_item_unauthorized(self, client, test_category):
        """Test creating menu item without authentication."""
        response = client.post(
            "/admin/products/",
            json={
                "name": "New Product",
                "price": 1500,
                "category_id": test_category.id
            }
        )
        assert response.status_code == 401
    
    def test_create_item_as_client(self, client, auth_headers, test_category):
        """Test creating menu item as regular client (should fail)."""
        response = client.post(
            "/admin/products/",
            json={
                "name": "New Product",
                "price": 1500,
                "category_id": test_category.id
            },
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_create_item_as_admin(self, client, admin_auth_headers, test_category):
        """Test creating menu item as admin."""
        response = client.post(
            "/admin/products/",
            json={
                "name": "New Product",
                "description": "New Description",
                "price": 1500,
                "category_id": test_category.id,
                "image_url": "https://example.com/new.jpg"
            },
            headers=admin_auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["price"] == 1500
        assert "id" in data
    
    def test_update_item_as_admin(self, client, admin_auth_headers, test_menu_item):
        """Test updating menu item as admin."""
        response = client.put(
            f"/admin/products/{test_menu_item.id}",
            json={
                "name": "Updated Product",
                "price": 2500
            },
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 2500
    
    def test_delete_item_as_admin(self, client, admin_auth_headers, test_menu_item):
        """Test deleting menu item as admin."""
        response = client.delete(
            f"/admin/products/{test_menu_item.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == 204
        
        # Verify item is deleted
        get_response = client.get("/products/")
        assert len(get_response.json()) == 0
