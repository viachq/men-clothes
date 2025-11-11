"""
Integration tests for shopping cart functionality.
Tests critical business logic for cart operations.
"""
import pytest


class TestCartOperations:
    """Tests for cart CRUD operations."""
    
    def test_get_empty_cart(self, client, auth_headers):
        """Test getting an empty cart."""
        response = client.get("/cart/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"] == []
    
    def test_cart_created_automatically(self, client, auth_headers, test_db, test_user):
        """Test that cart is created automatically for user."""
        from backend.models.cart import Cart
        
        # Initially no cart
        cart_before = test_db.query(Cart).filter(Cart.user_id == test_user.id).first()
        
        # Request cart
        response = client.get("/cart/me", headers=auth_headers)
        assert response.status_code == 200
        
        # Cart should be created
        cart_after = test_db.query(Cart).filter(Cart.user_id == test_user.id).first()
        assert cart_after is not None
    
    def test_add_item_to_cart(self, client, auth_headers, test_menu_item):
        """Test adding item to cart."""
        response = client.post("/cart/me/items", headers=auth_headers, json={
            "menu_item_id": test_menu_item.id,
            "quantity": 2,
            "price": test_menu_item.price
        })
        
        assert response.status_code == 200
        assert "id" in response.json()
        
        # Verify item in cart
        cart = client.get("/cart/me", headers=auth_headers).json()
        assert len(cart["items"]) == 1
        assert cart["items"][0]["menu_item_id"] == test_menu_item.id
        assert cart["items"][0]["quantity"] == 2
    
    def test_add_multiple_items(self, client, auth_headers, test_menu_items):
        """Test adding multiple items to cart."""
        for item in test_menu_items:
            response = client.post("/cart/me/items", headers=auth_headers, json={
                "menu_item_id": item.id,
                "quantity": 1,
                "price": item.price
            })
            assert response.status_code == 200
        
        # Check cart
        cart = client.get("/cart/me", headers=auth_headers).json()
        assert len(cart["items"]) == len(test_menu_items)
    
    def test_update_item_quantity(self, client, auth_headers, test_cart_item):
        """Test updating quantity of cart item."""
        new_quantity = 5
        response = client.put(
            f"/cart/me/items/{test_cart_item.id}",
            headers=auth_headers,
            json={"quantity": new_quantity}
        )
        
        assert response.status_code == 200
        
        # Verify update
        cart = client.get("/cart/me", headers=auth_headers).json()
        item = next(i for i in cart["items"] if i["id"] == test_cart_item.id)
        assert item["quantity"] == new_quantity
    
    def test_remove_item_from_cart(self, client, auth_headers, test_cart_item):
        """Test removing item from cart."""
        response = client.delete(
            f"/cart/me/items/{test_cart_item.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify removal
        cart = client.get("/cart/me", headers=auth_headers).json()
        assert not any(i["id"] == test_cart_item.id for i in cart["items"])
    
    def test_remove_nonexistent_item(self, client, auth_headers):
        """Test removing item that doesn't exist."""
        response = client.delete(
            "/cart/me/items/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_clear_cart(self, client, auth_headers, test_cart, test_cart_item):
        """Test clearing all items from cart."""
        # Add more items
        for i in range(2):
            client.post("/cart/me/items", headers=auth_headers, json={
                "menu_item_id": test_cart_item.menu_item_id,
                "quantity": 1,
                "price": 10000
            })
        
        # Clear cart
        response = client.delete("/cart/me", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify empty
        cart = client.get("/cart/me", headers=auth_headers).json()
        assert cart["items"] == []
    
    def test_update_nonexistent_cart_item(self, client, auth_headers):
        """Test updating item that doesn't exist in cart."""
        response = client.put(
            "/cart/me/items/99999",
            headers=auth_headers,
            json={"quantity": 5}
        )
        
        assert response.status_code == 404
    
    def test_cart_requires_authentication(self, client):
        """Test that all cart operations require authentication."""
        # Get cart
        assert client.get("/cart/me").status_code == 401
        
        # Add item
        assert client.post("/cart/me/items", json={
            "menu_item_id": 1,
            "quantity": 1,
            "price": 1000
        }).status_code == 401
        
        # Update item
        assert client.put("/cart/me/items/1", json={
            "quantity": 2
        }).status_code == 401
        
        # Remove item
        assert client.delete("/cart/me/items/1").status_code == 401
        
        # Clear cart
        assert client.delete("/cart/me").status_code == 401


class TestCartIsolation:
    """Tests for cart isolation between users."""
    
    def test_users_have_separate_carts(self, client, test_db):
        """Test that each user has their own cart."""
        from backend.models.user import User
        from backend.core.security import hash_password
        from backend.core.enums import UserRole
        
        # Create two users
        user1 = User(username="user1", password=hash_password("pass1"), role=UserRole.CLIENT.value)
        user2 = User(username="user2", password=hash_password("pass2"), role=UserRole.CLIENT.value)
        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()
        
        # Login both users
        token1 = client.post("/auth/login", json={"username": "user1", "password": "pass1"}).json()["access_token"]
        token2 = client.post("/auth/login", json={"username": "user2", "password": "pass2"}).json()["access_token"]
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User1 adds item
        client.post("/cart/me/items", headers=headers1, json={
            "menu_item_id": 1,
            "quantity": 2,
            "price": 1000
        })
        
        # User2's cart should be empty
        cart2 = client.get("/cart/me", headers=headers2).json()
        assert cart2["items"] == []
        
        # User1's cart should have the item
        cart1 = client.get("/cart/me", headers=headers1).json()
        assert len(cart1["items"]) == 1

