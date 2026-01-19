"""
Tests for order-service models.
"""
import pytest
from backend.models.cart import Cart, CartItem
from backend.models.order import Order
from backend.core.enums import OrderStatus, PaymentMethod


class TestCart:
    """Tests for Cart model."""
    
    def test_create_cart(self, test_db, test_user):
        """Test creating a cart."""
        cart = Cart(user_id=test_user.id)
        test_db.add(cart)
        test_db.commit()
        test_db.refresh(cart)
        
        assert cart.id is not None
        assert cart.user_id == test_user.id
    
    def test_cart_unique_user_id(self, test_db, test_user):
        """Test that cart user_id must be unique."""
        cart1 = Cart(user_id=test_user.id)
        test_db.add(cart1)
        test_db.commit()
        
        cart2 = Cart(user_id=test_user.id)
        test_db.add(cart2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestCartItem:
    """Tests for CartItem model."""
    
    def test_create_cart_item(self, test_db, test_cart):
        """Test creating a cart item."""
        item = CartItem(
            cart_id=test_cart.id,
            menu_item_id=1,
            quantity=2,
            price=1000
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        
        assert item.id is not None
        assert item.cart_id == test_cart.id
        assert item.menu_item_id == 1
        assert item.quantity == 2
        assert item.price == 1000


class TestOrder:
    """Tests for Order model."""
    
    def test_create_order(self, test_db, test_user):
        """Test creating an order."""
        order = Order(
            user_id=test_user.id,
            status=OrderStatus.PENDING.value,
            delivery_address="Test Address",
            payment_method=PaymentMethod.CARD.value,
            total_price=2000
        )
        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)
        
        assert order.id is not None
        assert order.user_id == test_user.id
        assert order.status == OrderStatus.PENDING.value
        assert order.delivery_address == "Test Address"
        assert order.payment_method == PaymentMethod.CARD.value
        assert order.total_price == 2000
