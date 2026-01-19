"""
Tests for database models.
"""
import pytest
from sqlalchemy.exc import IntegrityError

from backend.models.user import User
from backend.core.enums import UserRole
from backend.core.security import hash_password


class TestUserModel:
    """Tests for User model."""

    def test_create_user_with_required_fields(self, test_db):
        """Test creating user with required fields."""
        user = User(
            username="testuser",
            password=hash_password("password123"),
            role=UserRole.CLIENT.value
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.role == UserRole.CLIENT.value
        assert user.password is not None

    def test_user_username_unique(self, test_db):
        """Test that username must be unique."""
        user1 = User(
            username="uniqueuser",
            password=hash_password("pass1"),
            role=UserRole.CLIENT.value
        )
        test_db.add(user1)
        test_db.commit()

        # Try to create another user with same username
        user2 = User(
            username="uniqueuser",
            password=hash_password("pass2"),
            role=UserRole.CLIENT.value
        )
        test_db.add(user2)
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_user_default_role(self, test_db):
        """Test that user has CLIENT role by default."""
        user = User(
            username="defaultroleuser",
            password=hash_password("password123")
            # role not specified
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.role == UserRole.CLIENT.value

    def test_user_explicit_role(self, test_db):
        """Test creating user with explicit role."""
        user = User(
            username="adminuser",
            password=hash_password("password123"),
            role=UserRole.SYSTEM_ADMIN.value
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.role == UserRole.SYSTEM_ADMIN.value

    def test_user_all_roles(self, test_db):
        """Test creating users with all different roles."""
        roles = [UserRole.CLIENT, UserRole.MANAGER, UserRole.SYSTEM_ADMIN]
        for role in roles:
            user = User(
                username=f"user_{role.value}",
                password=hash_password("password123"),
                role=role.value
            )
            test_db.add(user)
        test_db.commit()

        # Verify all users were created
        users = test_db.query(User).all()
        assert len(users) >= 3
        usernames = [u.username for u in users]
        assert "user_client" in usernames
        assert "user_manager" in usernames
        assert "user_system_admin" in usernames

    def test_user_password_stored(self, test_db):
        """Test that password is stored in database."""
        password_hash = hash_password("mypassword")
        user = User(
            username="passworduser",
            password=password_hash,
            role=UserRole.CLIENT.value
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.password == password_hash
        assert user.password != "mypassword"  # Should be hashed

    def test_user_query_by_username(self, test_db):
        """Test querying user by username."""
        user = User(
            username="queryuser",
            password=hash_password("pass123"),
            role=UserRole.CLIENT.value
        )
        test_db.add(user)
        test_db.commit()

        found_user = test_db.query(User).filter(User.username == "queryuser").first()
        assert found_user is not None
        assert found_user.username == "queryuser"

    def test_user_query_by_id(self, test_db):
        """Test querying user by ID."""
        user = User(
            username="iduser",
            password=hash_password("pass123"),
            role=UserRole.CLIENT.value
        )
        test_db.add(user)
        test_db.commit()
        user_id = user.id

        found_user = test_db.query(User).filter(User.id == user_id).first()
        assert found_user is not None
        assert found_user.id == user_id

    def test_user_query_by_role(self, test_db):
        """Test querying users by role."""
        # Create users with different roles
        client_user = User(
            username="client1",
            password=hash_password("pass"),
            role=UserRole.CLIENT.value
        )
        manager_user = User(
            username="manager1",
            password=hash_password("pass"),
            role=UserRole.MANAGER.value
        )
        test_db.add(client_user)
        test_db.add(manager_user)
        test_db.commit()

        # Query by role
        clients = test_db.query(User).filter(User.role == UserRole.CLIENT.value).all()
        assert len(clients) >= 1
        assert any(u.username == "client1" for u in clients)

    def test_user_update(self, test_db):
        """Test updating user fields."""
        user = User(
            username="updateuser",
            password=hash_password("oldpass"),
            role=UserRole.CLIENT.value
        )
        test_db.add(user)
        test_db.commit()

        # Update user
        user.username = "updateduser"
        user.role = UserRole.MANAGER.value
        test_db.commit()
        test_db.refresh(user)

        assert user.username == "updateduser"
        assert user.role == UserRole.MANAGER.value
