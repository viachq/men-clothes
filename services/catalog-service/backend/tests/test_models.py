"""
Tests for catalog-service models.
"""
import pytest
from backend.models.category import Category
from backend.models.menu_item import MenuItem


class TestCategory:
    """Tests for Category model."""
    
    def test_create_category(self, test_db):
        """Test creating a category."""
        category = Category(name="Test Category")
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        assert category.id is not None
        assert category.name == "Test Category"
    
    def test_category_unique_name(self, test_db):
        """Test that category names must be unique."""
        category1 = Category(name="Unique Category")
        test_db.add(category1)
        test_db.commit()
        
        category2 = Category(name="Unique Category")
        test_db.add(category2)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestMenuItem:
    """Tests for MenuItem model."""
    
    def test_create_menu_item(self, test_db, test_category):
        """Test creating a menu item."""
        item = MenuItem(
            name="Test Product",
            description="Test Description",
            price=1000,
            category_id=test_category.id,
            image_url="https://example.com/image.jpg"
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        
        assert item.id is not None
        assert item.name == "Test Product"
        assert item.description == "Test Description"
        assert item.price == 1000
        assert item.category_id == test_category.id
        assert item.image_url == "https://example.com/image.jpg"
    
    def test_menu_item_without_category(self, test_db):
        """Test creating a menu item without category."""
        item = MenuItem(
            name="Standalone Product",
            price=2000
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        
        assert item.id is not None
        assert item.category_id is None
