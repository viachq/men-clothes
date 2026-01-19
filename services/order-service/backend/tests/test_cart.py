"""
Tests for cart endpoints.
"""
import pytest


class TestGetCart:
    """Tests for GET /cart/me endpoint."""
    
    def test_get_cart_unauthorized(self, client):
        """Test getting cart without authentication."""
        response = client.get("/cart/me")
        assert response.status_code == 401
    
    def test_get_cart_empty(self, client, auth_headers):
        """Test getting empty cart."""
        response = client.get("/cart/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
        assert data["items"] == []
    
    def test_get_cart_with_items(self, client, auth_headers, test_cart_item):
        """Test getting cart with items."""
        response = client.get("/cart/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["menu_item_id"] == test_cart_item.menu_item_id
        assert data["items"][0]["quantity"] == test_cart_item.quantity


class TestAddCartItem:
    """Tests for POST /cart/me/items endpoint."""
    
    def test_add_item_unauthorized(self, client):
        """Test adding item without authentication."""
        response = client.post(
            "/cart/me/items",
            json={"menu_item_id": 1, "quantity": 1, "price": 1000}
        )
        assert response.status_code == 401
    
    def test_add_item(self, client, auth_headers):
        """Test adding item to cart."""
        response = client.post(
            "/cart/me/items",
            json={"menu_item_id": 1, "quantity": 2, "price": 1000},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Item added"


class TestUpdateCartItem:
    """Tests for PUT /cart/me/items/{cart_item_id} endpoint."""
    
    def test_update_item_unauthorized(self, client, test_cart_item):
        """Test updating item without authentication."""
        response = client.put(
            f"/cart/me/items/{test_cart_item.id}",
            json={"quantity": 5}
        )
        assert response.status_code == 401
    
    def test_update_item(self, client, auth_headers, test_cart_item):
        """Test updating item quantity."""
        response = client.put(
            f"/cart/me/items/{test_cart_item.id}",
            json={"quantity": 5},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Quantity updated"
        
        # Verify update
        get_response = client.get("/cart/me", headers=auth_headers)
        items = get_response.json()["items"]
        assert items[0]["quantity"] == 5
    
    def test_update_item_not_found(self, client, auth_headers):
        """Test updating non-existent item."""
        response = client.put(
            "/cart/me/items/999",
            json={"quantity": 5},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestDeleteCartItem:
    """Tests for DELETE /cart/me/items/{cart_item_id} endpoint."""
    
    def test_delete_item_unauthorized(self, client, test_cart_item):
        """Test deleting item without authentication."""
        response = client.delete(f"/cart/me/items/{test_cart_item.id}")
        assert response.status_code == 401
    
    def test_delete_item(self, client, auth_headers, test_cart_item):
        """Test deleting item from cart."""
        response = client.delete(
            f"/cart/me/items/{test_cart_item.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get("/cart/me", headers=auth_headers)
        assert len(get_response.json()["items"]) == 0
