"""
Tests for order-service security functions.
"""
import pytest
from backend.core.security import decode_token
from backend.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from datetime import datetime, timedelta, timezone
from jose import jwt


class TestDecodeToken:
    """Tests for decode_token function."""
    
    def test_decode_token_valid(self):
        """Test decoding a valid token."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        token_data = {"sub": "testuser", "exp": expire}
        token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        result = decode_token(token)
        assert result is not None
        assert result["sub"] == "testuser"
    
    def test_decode_token_invalid(self):
        """Test decoding an invalid token."""
        result = decode_token("invalid.token.here")
        assert result is None
    
    def test_decode_token_none(self):
        """Test decoding None token."""
        result = decode_token(None)
        assert result is None
    
    def test_decode_token_expired(self):
        """Test decoding an expired token."""
        expire = datetime.now(timezone.utc) - timedelta(minutes=1)
        token_data = {"sub": "testuser", "exp": expire}
        token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        result = decode_token(token)
        assert result is None
