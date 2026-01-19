"""
Tests for dependency injection functions.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch
from backend.deps import get_current_user, require_roles
from backend.core.enums import UserRole
from backend.models.user import User


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""
    
    def test_get_current_user_no_token(self):
        """Test get_current_user without token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(creds=None)
        assert exc_info.value.status_code == 401
    
    def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token."""
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )
        
        with patch('backend.deps.decode_token', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(creds=creds)
            assert exc_info.value.status_code == 401
    
    def test_get_current_user_valid_token(self):
        """Test get_current_user with valid token."""
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token"
        )
        
        mock_user_data = {"id": 1, "username": "testuser", "role": "CLIENT"}
        
        with patch('backend.deps.decode_token', return_value={"sub": "testuser"}):
            with patch('backend.deps.get_auth_client') as mock_get_client:
                mock_client = Mock()
                mock_client.get_user_by_username.return_value = mock_user_data
                mock_get_client.return_value = mock_client
                
                user = get_current_user(creds=creds)
                assert user.username == "testuser"
                assert user.role == "CLIENT"


class TestRequireRoles:
    """Tests for require_roles dependency."""
    
    def test_require_roles_allowed(self):
        """Test require_roles with allowed role."""
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token"
        )
        
        mock_user = User(id=1, username="admin", role=UserRole.SYSTEM_ADMIN.value)
        
        with patch('backend.deps.get_current_user', return_value=mock_user):
            role_checker = require_roles(UserRole.SYSTEM_ADMIN)
            result = role_checker(user=mock_user)
            assert result == mock_user
    
    def test_require_roles_forbidden(self):
        """Test require_roles with forbidden role."""
        mock_user = User(id=1, username="client", role=UserRole.CLIENT.value)
        
        role_checker = require_roles(UserRole.SYSTEM_ADMIN, UserRole.MANAGER)
        with pytest.raises(HTTPException) as exc_info:
            role_checker(user=mock_user)
        assert exc_info.value.status_code == 403
