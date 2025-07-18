#!/usr/bin/env python3
"""
Tests for API authentication functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import jwt
from datetime import datetime, timedelta

# Import the auth module
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_auth import AuthManager
from api_models import UserCreate, User

class TestAuthManagerInitialization:
    """Test AuthManager initialization"""
    
    def test_auth_manager_init_success(self):
        """Test successful AuthManager initialization"""
        # Mock database
        mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            auth_manager = AuthManager(mock_db)
            
            assert auth_manager.db == mock_db
            assert auth_manager.secret_key == 'test_secret_key_32_chars_long'
            assert auth_manager.algorithm == "HS256"
            assert auth_manager.access_token_expire_minutes == 1440
    
    def test_auth_manager_init_missing_secret(self):
        """Test AuthManager initialization without secret key"""
        # Mock database
        mock_db = MagicMock()
        
        # Mock environment without secret key
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="JWT_SECRET_KEY environment variable not set"):
                AuthManager(mock_db)

class TestPasswordOperations:
    """Test password hashing and verification"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock database
        self.mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            self.auth_manager = AuthManager(self.mock_db)
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password"
        hashed = self.auth_manager.hash_password(password)
        
        # Verify hash is different from original password
        assert hashed != password
        assert len(hashed) > len(password)
        assert hashed.startswith('$2b$')  # bcrypt format
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password"
        hashed = self.auth_manager.hash_password(password)
        
        # Verify correct password
        assert self.auth_manager.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password"
        hashed = self.auth_manager.hash_password(password)
        
        # Verify incorrect password
        assert self.auth_manager.verify_password("wrong_password", hashed) is False
    
    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        password = "test_password"
        hashed = self.auth_manager.hash_password(password)
        
        # Verify empty password
        assert self.auth_manager.verify_password("", hashed) is False

class TestTokenOperations:
    """Test JWT token operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock database
        self.mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            self.auth_manager = AuthManager(self.mock_db)
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "123", "username": "testuser"}
        token = self.auth_manager.create_access_token(data)
        
        # Verify token is created
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        decoded = jwt.decode(token, self.auth_manager.secret_key, algorithms=[self.auth_manager.algorithm])
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"
        assert "exp" in decoded
    
    def test_create_access_token_with_expiry(self):
        """Test access token creation with custom expiry"""
        data = {"sub": "123", "username": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = self.auth_manager.create_access_token(data, expires_delta)
        
        # Verify token can be decoded
        decoded = jwt.decode(token, self.auth_manager.secret_key, algorithms=[self.auth_manager.algorithm])
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"
    
    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        data = {"sub": "123", "username": "testuser"}
        token = self.auth_manager.create_access_token(data)
        
        # Verify valid token
        result = self.auth_manager.verify_token(token)
        assert result is not None
        assert result["sub"] == "123"
        assert result["username"] == "testuser"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        # Test with invalid token
        result = self.auth_manager.verify_token("invalid_token")
        assert result is None
    
    def test_verify_token_expired(self):
        """Test token verification with expired token"""
        # Create expired token
        data = {"sub": "123", "username": "testuser"}
        expires_delta = timedelta(minutes=-1)  # Expired
        token = self.auth_manager.create_access_token(data, expires_delta)
        
        # Verify expired token
        result = self.auth_manager.verify_token(token)
        assert result is None

class TestUserManagement:
    """Test user management operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock database
        self.mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            self.auth_manager = AuthManager(self.mock_db)
    
    @patch('api_auth.AuthManager.hash_password')
    async def test_create_user_success(self, mock_hash_password):
        """Test successful user creation"""
        # Mock password hashing
        mock_hash_password.return_value = "hashed_password"
        
        # Mock database operations
        self.mock_db.get_user_by_username.return_value = None
        self.mock_db.create_user.return_value = {
            'id': 1,
            'username': 'testuser',
            'created_at': '2023-01-01T00:00:00'
        }
        
        # Create user data
        user_data = UserCreate(username="testuser", password="testpassword")
        
        # Test user creation
        result = await self.auth_manager.create_user(user_data)
        
        assert isinstance(result, User)
        assert result.id == 1
        assert result.username == 'testuser'
        
        # Verify database calls
        self.mock_db.get_user_by_username.assert_called_once_with('testuser')
        self.mock_db.create_user.assert_called_once_with('testuser', 'hashed_password')
    
    @patch('api_auth.AuthManager.hash_password')
    async def test_create_user_duplicate_username(self, mock_hash_password):
        """Test user creation with duplicate username"""
        # Mock password hashing
        mock_hash_password.return_value = "hashed_password"
        
        # Mock existing user
        self.mock_db.get_user_by_username.return_value = {'id': 1, 'username': 'testuser'}
        
        # Create user data
        user_data = UserCreate(username="testuser", password="testpassword")
        
        # Test user creation with duplicate username
        with pytest.raises(ValueError, match="Username already exists"):
            await self.auth_manager.create_user(user_data)
    
    async def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Mock user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'password_hash': self.auth_manager.hash_password('testpassword')
        }
        self.mock_db.get_user_by_username.return_value = user_data
        
        # Test authentication
        token = await self.auth_manager.authenticate_user('testuser', 'testpassword')
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token content
        decoded = jwt.decode(token, self.auth_manager.secret_key, algorithms=[self.auth_manager.algorithm])
        assert decoded["sub"] == "1"
        assert decoded["username"] == "testuser"
    
    async def test_authenticate_user_invalid_username(self):
        """Test authentication with invalid username"""
        # Mock user not found
        self.mock_db.get_user_by_username.return_value = None
        
        # Test authentication
        token = await self.auth_manager.authenticate_user('nonexistent', 'testpassword')
        
        assert token is None
    
    async def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password"""
        # Mock user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'password_hash': self.auth_manager.hash_password('correctpassword')
        }
        self.mock_db.get_user_by_username.return_value = user_data
        
        # Test authentication with wrong password
        token = await self.auth_manager.authenticate_user('testuser', 'wrongpassword')
        
        assert token is None

class TestCurrentUserOperations:
    """Test current user operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock database
        self.mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            self.auth_manager = AuthManager(self.mock_db)
    
    async def test_get_current_user_success(self):
        """Test getting current user with valid token"""
        # Create valid token
        token_data = {"sub": "123", "username": "testuser"}
        token = self.auth_manager.create_access_token(token_data)
        
        # Mock user data
        user_data = {
            'id': 123,
            'username': 'testuser',
            'created_at': '2023-01-01T00:00:00'
        }
        self.mock_db.get_user_by_id.return_value = user_data
        
        # Test getting current user
        result = await self.auth_manager.get_current_user(token)
        
        assert isinstance(result, User)
        assert result.id == 123
        assert result.username == 'testuser'
        
        # Verify database call
        self.mock_db.get_user_by_id.assert_called_once_with(123)
    
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        # Test with invalid token
        result = await self.auth_manager.get_current_user("invalid_token")
        
        assert result is None
    
    async def test_get_current_user_user_not_found(self):
        """Test getting current user when user doesn't exist"""
        # Create valid token
        token_data = {"sub": "123", "username": "testuser"}
        token = self.auth_manager.create_access_token(token_data)
        
        # Mock user not found
        self.mock_db.get_user_by_id.return_value = None
        
        # Test getting current user
        result = await self.auth_manager.get_current_user(token)
        
        assert result is None
    
    async def test_get_current_user_missing_sub(self):
        """Test getting current user with token missing sub field"""
        # Create token without sub field
        token_data = {"username": "testuser"}
        token = self.auth_manager.create_access_token(token_data)
        
        # Test getting current user
        result = await self.auth_manager.get_current_user(token)
        
        assert result is None

class TestTokenRefresh:
    """Test token refresh operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock database
        self.mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            self.auth_manager = AuthManager(self.mock_db)
    
    async def test_refresh_token_success(self):
        """Test successful token refresh"""
        # Create original token
        original_data = {"sub": "123", "username": "testuser"}
        original_token = self.auth_manager.create_access_token(original_data)
        
        # Test token refresh
        new_token = await self.auth_manager.refresh_token(original_token)
        
        assert new_token is not None
        assert new_token != original_token
        
        # Verify new token content
        decoded = jwt.decode(new_token, self.auth_manager.secret_key, algorithms=[self.auth_manager.algorithm])
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"
    
    async def test_refresh_token_invalid(self):
        """Test token refresh with invalid token"""
        # Test with invalid token
        new_token = await self.auth_manager.refresh_token("invalid_token")
        
        assert new_token is None

class TestPasswordChange:
    """Test password change operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock database
        self.mock_db = MagicMock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret_key_32_chars_long'}):
            self.auth_manager = AuthManager(self.mock_db)
    
    @patch('api_auth.AuthManager.hash_password')
    async def test_change_password_success(self, mock_hash_password):
        """Test successful password change"""
        # Mock password hashing
        mock_hash_password.return_value = "new_hashed_password"
        
        # Mock user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'password_hash': self.auth_manager.hash_password('oldpassword')
        }
        self.mock_db.get_user_by_id.return_value = user_data
        
        # Test password change
        result = await self.auth_manager.change_password(1, 'oldpassword', 'newpassword')
        
        assert result is True
        
        # Verify database calls
        self.mock_db.get_user_by_id.assert_called_once_with(1)
        self.mock_db.execute.assert_called_once()
    
    async def test_change_password_user_not_found(self):
        """Test password change with non-existent user"""
        # Mock user not found
        self.mock_db.get_user_by_id.return_value = None
        
        # Test password change
        result = await self.auth_manager.change_password(999, 'oldpassword', 'newpassword')
        
        assert result is False
    
    async def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        # Mock user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'password_hash': self.auth_manager.hash_password('correctoldpassword')
        }
        self.mock_db.get_user_by_id.return_value = user_data
        
        # Test password change with wrong old password
        result = await self.auth_manager.change_password(1, 'wrongoldpassword', 'newpassword')
        
        assert result is False

if __name__ == "__main__":
    pytest.main([__file__]) 