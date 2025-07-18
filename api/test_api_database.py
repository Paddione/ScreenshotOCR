#!/usr/bin/env python3
"""
Tests for API database functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import os

# Import the database module
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_database import Database

class TestDatabaseConnection:
    """Test database connection functionality"""
    
    @patch('api_database.asyncpg.create_pool')
    async def test_database_connection(self, mock_create_pool):
        """Test database connection creation"""
        # Mock connection pool
        mock_pool = AsyncMock()
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            assert db.pool is not None
            mock_create_pool.assert_called_once()
    
    def test_database_url_missing(self):
        """Test database initialization without URL"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL environment variable not set"):
                Database()
    
    @patch('api_database.asyncpg.create_pool')
    async def test_database_disconnect(self, mock_create_pool):
        """Test database disconnection"""
        # Mock connection pool
        mock_pool = AsyncMock()
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            await db.disconnect()
            
            mock_pool.close.assert_called_once()

class TestDatabaseOperations:
    """Test database operation methods"""
    
    @patch('api_database.asyncpg.create_pool')
    async def test_execute_query(self, mock_create_pool):
        """Test execute query method"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test execute
            await db.execute("SELECT * FROM test", 1, 2)
            mock_conn.execute.assert_called_once_with("SELECT * FROM test", 1, 2)
    
    @patch('api_database.asyncpg.create_pool')
    async def test_fetch_query(self, mock_create_pool):
        """Test fetch query method"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetch result
        mock_row = MagicMock()
        mock_row.__dict__ = {'id': 1, 'name': 'test'}
        mock_conn.fetch.return_value = [mock_row]
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test fetch
            result = await db.fetch("SELECT * FROM test")
            assert len(result) == 1
            assert result[0]['id'] == 1
            assert result[0]['name'] == 'test'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_fetchrow_query(self, mock_create_pool):
        """Test fetchrow query method"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchrow result
        mock_row = MagicMock()
        mock_row.__dict__ = {'id': 1, 'name': 'test'}
        mock_conn.fetchrow.return_value = mock_row
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test fetchrow
            result = await db.fetchrow("SELECT * FROM test WHERE id = $1", 1)
            assert result['id'] == 1
            assert result['name'] == 'test'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_fetchval_query(self, mock_create_pool):
        """Test fetchval query method"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchval result
        mock_conn.fetchval.return_value = 42
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test fetchval
            result = await db.fetchval("SELECT COUNT(*) FROM test")
            assert result == 42

class TestTableCreation:
    """Test database table creation"""
    
    @patch('api_database.asyncpg.create_pool')
    async def test_create_tables(self, mock_create_pool):
        """Test table creation"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test create tables
            await db.create_tables()
            
            # Verify all table creation calls
            assert mock_conn.execute.call_count >= 6  # Users, folders, responses tables + indexes

class TestUserOperations:
    """Test user-related database operations"""
    
    @patch('api_database.asyncpg.create_pool')
    async def test_create_user(self, mock_create_pool):
        """Test user creation"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchrow result
        mock_row = MagicMock()
        mock_row.__dict__ = {'id': 1, 'username': 'testuser', 'created_at': '2023-01-01T00:00:00'}
        mock_conn.fetchrow.return_value = mock_row
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test create user
            result = await db.create_user('testuser', 'hashed_password')
            assert result['id'] == 1
            assert result['username'] == 'testuser'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_get_user_by_username(self, mock_create_pool):
        """Test getting user by username"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchrow result
        mock_row = MagicMock()
        mock_row.__dict__ = {'id': 1, 'username': 'testuser', 'password_hash': 'hash'}
        mock_conn.fetchrow.return_value = mock_row
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test get user by username
            result = await db.get_user_by_username('testuser')
            assert result['id'] == 1
            assert result['username'] == 'testuser'
            assert result['password_hash'] == 'hash'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_get_user_by_id(self, mock_create_pool):
        """Test getting user by ID"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchrow result
        mock_row = MagicMock()
        mock_row.__dict__ = {'id': 1, 'username': 'testuser', 'password_hash': 'hash'}
        mock_conn.fetchrow.return_value = mock_row
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test get user by ID
            result = await db.get_user_by_id(1)
            assert result['id'] == 1
            assert result['username'] == 'testuser'

class TestFolderOperations:
    """Test folder-related database operations"""
    
    @patch('api_database.asyncpg.create_pool')
    async def test_create_folder(self, mock_create_pool):
        """Test folder creation"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchrow result
        mock_row = MagicMock()
        mock_row.__dict__ = {'id': 1, 'user_id': 1, 'name': 'Test Folder', 'created_at': '2023-01-01T00:00:00'}
        mock_conn.fetchrow.return_value = mock_row
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test create folder
            result = await db.create_folder(1, 'Test Folder')
            assert result['id'] == 1
            assert result['name'] == 'Test Folder'
            assert result['user_id'] == 1
    
    @patch('api_database.asyncpg.create_pool')
    async def test_get_folders_by_user(self, mock_create_pool):
        """Test getting folders by user"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetch result
        mock_row1 = MagicMock()
        mock_row1.__dict__ = {'id': 1, 'name': 'Folder 1', 'user_id': 1}
        mock_row2 = MagicMock()
        mock_row2.__dict__ = {'id': 2, 'name': 'Folder 2', 'user_id': 1}
        mock_conn.fetch.return_value = [mock_row1, mock_row2]
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test get folders by user
            result = await db.get_folders_by_user(1)
            assert len(result) == 2
            assert result[0]['name'] == 'Folder 1'
            assert result[1]['name'] == 'Folder 2'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_delete_folder(self, mock_create_pool):
        """Test folder deletion"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock execute result
        mock_conn.execute.return_value = "DELETE 1"
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test delete folder
            result = await db.delete_folder(1, 1)
            assert result is True

class TestResponseOperations:
    """Test response-related database operations"""
    
    @patch('api_database.asyncpg.create_pool')
    async def test_create_response(self, mock_create_pool):
        """Test response creation"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchrow result
        mock_row = MagicMock()
        mock_row.__dict__ = {
            'id': 1, 'user_id': 1, 'folder_id': 1, 
            'ocr_text': 'Test text', 'ai_response': 'AI analysis',
            'image_path': '/path/to/image.png', 'created_at': '2023-01-01T00:00:00'
        }
        mock_conn.fetchrow.return_value = mock_row
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test create response
            result = await db.create_response(1, 1, 'Test text', 'AI analysis', '/path/to/image.png')
            assert result['id'] == 1
            assert result['ocr_text'] == 'Test text'
            assert result['ai_response'] == 'AI analysis'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_get_responses_by_user(self, mock_create_pool):
        """Test getting responses by user"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetch result
        mock_row = MagicMock()
        mock_row.__dict__ = {
            'id': 1, 'ocr_text': 'Test text', 'ai_response': 'AI analysis',
            'folder_id': 1, 'folder_name': 'Test Folder', 'created_at': '2023-01-01T00:00:00'
        }
        mock_conn.fetch.return_value = [mock_row]
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test get responses by user
            result = await db.get_responses_by_user(1, 10, 0)
            assert len(result) == 1
            assert result[0]['ocr_text'] == 'Test text'
            assert result[0]['folder_name'] == 'Test Folder'
    
    @patch('api_database.asyncpg.create_pool')
    async def test_count_responses_by_user(self, mock_create_pool):
        """Test counting responses by user"""
        # Mock connection pool and connection
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock fetchval result
        mock_conn.fetchval.return_value = 5
        mock_create_pool.return_value = mock_pool
        
        # Mock environment variable
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db = Database()
            await db.connect()
            
            # Test count responses by user
            result = await db.count_responses_by_user(1)
            assert result == 5

if __name__ == "__main__":
    pytest.main([__file__]) 