#!/usr/bin/env python3
"""
Tests for storage processor functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
import asyncio

# Import the storage processor module
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage_processor import StorageProcessor

class TestStorageProcessorInitialization:
    """Test StorageProcessor initialization"""
    
    def test_storage_processor_init_success(self):
        """Test successful StorageProcessor initialization"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            processor = StorageProcessor()
            
            assert processor.redis_url == 'redis://localhost:6379'
            assert processor.database_url == 'postgresql://test:test@localhost/test'
    
    def test_storage_processor_init_missing_database_url(self):
        """Test StorageProcessor initialization without database URL"""
        # Mock environment without database URL
        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL environment variable not set"):
                StorageProcessor()

class TestStorageProcessorConnection:
    """Test storage processor connection functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            self.processor = StorageProcessor()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_start_processing_success(self, mock_database_class, mock_redis_from_url):
        """Test successful processing start"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock connections
        mock_redis_client.ping.return_value = True
        mock_db.execute.return_value = "SELECT 1"
        
        # Mock processing loop to return early
        with patch.object(self.processor, 'processing_loop', new_callable=AsyncMock) as mock_loop:
            mock_loop.side_effect = Exception("Test exit")
            
            # Test processing start
            with pytest.raises(Exception, match="Test exit"):
                await self.processor.start_processing()
            
            # Verify Redis connection
            mock_redis_from_url.assert_called_once_with(
                'redis://localhost:6379', 
                encoding="utf-8", 
                decode_responses=True
            )
            mock_redis_client.ping.assert_called_once()
            
            # Verify database connection
            mock_database_class.assert_called_once()
            mock_db.connect.assert_called_once()
            mock_db.execute.assert_called_once_with("SELECT 1")
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_start_processing_redis_error(self, mock_database_class, mock_redis_from_url):
        """Test processing start with Redis error"""
        # Mock Redis client with error
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock Redis ping to fail
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        
        # Test processing start
        with pytest.raises(Exception, match="Redis connection failed"):
            await self.processor.start_processing()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_start_processing_database_error(self, mock_database_class, mock_redis_from_url):
        """Test processing start with database error"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database with error
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock connections
        mock_redis_client.ping.return_value = True
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # Test processing start
        with pytest.raises(Exception, match="Database connection failed"):
            await self.processor.start_processing()

class TestStorageProcessorLoop:
    """Test storage processing loop functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            self.processor = StorageProcessor()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_processing_loop_with_job(self, mock_database_class, mock_redis_from_url):
        """Test processing loop with job data"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock job data
        job_data = {
            'user_id': 1,
            'folder_id': 1,
            'ocr_text': 'Test OCR text',
            'ai_response': 'Test AI response',
            'image_path': '/path/to/image.png',
            'ocr_confidence': 85.5,
            'ocr_language': 'english',
            'ai_model': 'gpt-4',
            'ai_tokens': 150
        }
        mock_redis_client.brpop.return_value = ('storage_queue', json.dumps(job_data))
        
        # Mock store_response
        with patch.object(self.processor, 'store_response', new_callable=AsyncMock) as mock_store:
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                ('storage_queue', json.dumps(job_data)),
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.processor.processing_loop()
            
            # Verify job processing
            mock_store.assert_called_once_with(job_data)
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_processing_loop_no_job(self, mock_database_class, mock_redis_from_url):
        """Test processing loop with no job data"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock no job data (timeout)
        mock_redis_client.brpop.return_value = None
        
        # Mock store_response
        with patch.object(self.processor, 'store_response', new_callable=AsyncMock) as mock_store:
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                None,
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.processor.processing_loop()
            
            # Verify no job processing
            mock_store.assert_not_called()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_processing_loop_invalid_json(self, mock_database_class, mock_redis_from_url):
        """Test processing loop with invalid JSON"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock invalid JSON data
        mock_redis_client.brpop.return_value = ('storage_queue', 'invalid json')
        
        # Mock store_response
        with patch.object(self.processor, 'store_response', new_callable=AsyncMock) as mock_store:
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                ('storage_queue', 'invalid json'),
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.processing_loop()
            
            # Verify no job processing due to JSON error
            mock_store.assert_not_called()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_processing_loop_store_error(self, mock_database_class, mock_redis_from_url):
        """Test processing loop with storage error"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock job data
        job_data = {
            'user_id': 1,
            'folder_id': 1,
            'ocr_text': 'Test OCR text',
            'ai_response': 'Test AI response',
            'image_path': '/path/to/image.png',
            'ocr_confidence': 85.5,
            'ocr_language': 'english',
            'ai_model': 'gpt-4',
            'ai_tokens': 150
        }
        mock_redis_client.brpop.return_value = ('storage_queue', json.dumps(job_data))
        
        # Mock store_response to raise error
        with patch.object(self.processor, 'store_response', new_callable=AsyncMock) as mock_store:
            mock_store.side_effect = Exception("Storage error")
            
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                ('storage_queue', json.dumps(job_data)),
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.processor.processing_loop()
            
            # Verify job processing was attempted
            mock_store.assert_called_once_with(job_data)

class TestStorageOperations:
    """Test storage operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            self.processor = StorageProcessor()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_store_response_success(self, mock_database_class, mock_redis_from_url):
        """Test successful response storage"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock database fetchval
        mock_db.fetchval.return_value = 12345
        
        # Test storage
        job_data = {
            'user_id': 1,
            'folder_id': 1,
            'ocr_text': 'Test OCR text',
            'ai_response': 'Test AI response',
            'image_path': '/path/to/image.png',
            'ocr_confidence': 85.5,
            'ocr_language': 'english',
            'ai_model': 'gpt-4',
            'ai_tokens': 150
        }
        
        await self.processor.store_response(job_data)
        
        # Verify database call
        mock_db.fetchval.assert_called_once()
        call_args = mock_db.fetchval.call_args
        assert call_args[0][0].startswith("INSERT INTO responses")
        assert call_args[0][1] == 1  # user_id
        assert call_args[0][2] == 1  # folder_id
        assert call_args[0][3] == 'Test OCR text'  # ocr_text
        assert call_args[0][4] == 'Test AI response'  # ai_response
        assert call_args[0][5] == '/path/to/image.png'  # image_path
        assert call_args[0][6] == 85.5  # ocr_confidence
        assert call_args[0][7] == 'english'  # ocr_language
        assert call_args[0][8] == 'gpt-4'  # ai_model
        assert call_args[0][9] == 150  # ai_tokens
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_store_response_missing_user_id(self, mock_database_class, mock_redis_from_url):
        """Test response storage with missing user ID"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Test storage with missing user_id
        job_data = {
            'folder_id': 1,
            'ocr_text': 'Test OCR text',
            'ai_response': 'Test AI response',
            'image_path': '/path/to/image.png',
            'ocr_confidence': 85.5,
            'ocr_language': 'english',
            'ai_model': 'gpt-4',
            'ai_tokens': 150
        }
        
        await self.processor.store_response(job_data)
        
        # Verify no database call due to missing user_id
        mock_db.fetchval.assert_not_called()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_store_response_database_error(self, mock_database_class, mock_redis_from_url):
        """Test response storage with database error"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database with error
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock database fetchval to raise error
        mock_db.fetchval.side_effect = Exception("Database error")
        
        # Test storage
        job_data = {
            'user_id': 1,
            'folder_id': 1,
            'ocr_text': 'Test OCR text',
            'ai_response': 'Test AI response',
            'image_path': '/path/to/image.png',
            'ocr_confidence': 85.5,
            'ocr_language': 'english',
            'ai_model': 'gpt-4',
            'ai_tokens': 150
        }
        
        # Test that error is raised
        with pytest.raises(Exception, match="Database error"):
            await self.processor.store_response(job_data)
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_store_response_with_none_values(self, mock_database_class, mock_redis_from_url):
        """Test response storage with None values"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock database fetchval
        mock_db.fetchval.return_value = 12345
        
        # Test storage with None values
        job_data = {
            'user_id': 1,
            'folder_id': None,
            'ocr_text': '',
            'ai_response': 'Test AI response',
            'image_path': '',
            'ocr_confidence': 0,
            'ocr_language': 'unknown',
            'ai_model': 'unknown',
            'ai_tokens': 0
        }
        
        await self.processor.store_response(job_data)
        
        # Verify database call with None values
        mock_db.fetchval.assert_called_once()
        call_args = mock_db.fetchval.call_args
        assert call_args[0][1] == 1  # user_id
        assert call_args[0][2] is None  # folder_id
        assert call_args[0][3] == ''  # ocr_text
        assert call_args[0][4] == 'Test AI response'  # ai_response
        assert call_args[0][5] == ''  # image_path
        assert call_args[0][6] == 0  # ocr_confidence
        assert call_args[0][7] == 'unknown'  # ocr_language
        assert call_args[0][8] == 'unknown'  # ai_model
        assert call_args[0][9] == 0  # ai_tokens

class TestCleanup:
    """Test cleanup operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            self.processor = StorageProcessor()
    
    @patch('storage_processor.redis.from_url')
    @patch('storage_processor.Database')
    async def test_cleanup_on_exit(self, mock_database_class, mock_redis_from_url):
        """Test cleanup operations on exit"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock database
        mock_db = AsyncMock()
        mock_database_class.return_value = mock_db
        
        # Mock connections
        mock_redis_client.ping.return_value = True
        mock_db.execute.return_value = "SELECT 1"
        
        # Mock processing loop to return early
        with patch.object(self.processor, 'processing_loop', new_callable=AsyncMock) as mock_loop:
            mock_loop.side_effect = Exception("Test exit")
            
            # Test processing start and cleanup
            with pytest.raises(Exception, match="Test exit"):
                await self.processor.start_processing()
            
            # Verify cleanup
            mock_redis_client.close.assert_called_once()
            mock_db.disconnect.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__]) 