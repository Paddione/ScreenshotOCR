#!/usr/bin/env python3
"""
Tests for API routes functionality
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
import tempfile
import os

# Import the app from api_main
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_main import app

client = TestClient(app)

class TestFolderEndpoints:
    """Test folder management endpoints"""
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.get_folders_by_user')
    async def test_get_folders(self, mock_get_folders, mock_get_user):
        """Test getting user folders"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock folders response
        mock_folders = [
            {'id': 1, 'name': 'Test Folder', 'user_id': 1, 'created_at': '2023-01-01T00:00:00'}
        ]
        mock_get_folders.return_value = mock_folders
        
        response = client.get("/folders", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Test Folder'
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.create_folder')
    async def test_create_folder(self, mock_create_folder, mock_get_user):
        """Test creating a new folder"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock folder creation
        mock_folder = {'id': 1, 'name': 'New Folder', 'user_id': 1, 'created_at': '2023-01-01T00:00:00'}
        mock_create_folder.return_value = mock_folder
        
        response = client.post(
            "/folders",
            json={"name": "New Folder"},
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'New Folder'
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.delete_folder')
    async def test_delete_folder(self, mock_delete_folder, mock_get_user):
        """Test deleting a folder"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock folder deletion
        mock_delete_folder.return_value = True
        
        response = client.delete(
            "/folders/1",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Folder deleted successfully'

class TestResponseEndpoints:
    """Test response management endpoints"""
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.get_responses_by_user')
    @patch('api_main.db.count_responses_by_user')
    async def test_get_responses(self, mock_count, mock_get_responses, mock_get_user):
        """Test getting user responses"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock responses
        mock_responses = [
            {
                'id': 1,
                'ocr_text': 'Test text',
                'ai_response': 'AI analysis',
                'folder_id': 1,
                'folder_name': 'Test Folder',
                'created_at': '2023-01-01T00:00:00'
            }
        ]
        mock_get_responses.return_value = mock_responses
        mock_count.return_value = 1
        
        response = client.get("/responses", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 1
        assert len(data['items']) == 1
        assert data['items'][0]['ocr_text'] == 'Test text'
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.get_response_by_id')
    async def test_get_response(self, mock_get_response, mock_get_user):
        """Test getting a specific response"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock response
        mock_response = {
            'id': 1,
            'ocr_text': 'Test text',
            'ai_response': 'AI analysis',
            'folder_id': 1,
            'folder_name': 'Test Folder',
            'created_at': '2023-01-01T00:00:00'
        }
        mock_get_response.return_value = mock_response
        
        response = client.get("/responses/1", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == 1
        assert data['ocr_text'] == 'Test text'
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.delete_response')
    async def test_delete_response(self, mock_delete_response, mock_get_user):
        """Test deleting a response"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock response deletion
        mock_delete_response.return_value = True
        
        response = client.delete("/responses/1", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Response deleted successfully'

class TestUploadEndpoints:
    """Test file upload endpoints"""
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.redis_client.lpush')
    async def test_manual_upload(self, mock_redis, mock_get_user):
        """Test manual file upload"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock Redis
        mock_redis.return_value = 1
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(b'fake image data')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/upload",
                    files={"image": ("test.png", f, "image/png")},
                    headers={"Authorization": "Bearer test_token"}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data['message'] == 'File uploaded successfully'
        finally:
            os.unlink(tmp_file_path)

class TestExportEndpoints:
    """Test PDF export endpoints"""
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.get_response_by_id')
    async def test_export_pdf(self, mock_get_response, mock_get_user):
        """Test PDF export functionality"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock response
        mock_response = {
            'id': 1,
            'ocr_text': 'Test text',
            'ai_response': 'AI analysis',
            'folder_id': 1,
            'folder_name': 'Test Folder',
            'created_at': '2023-01-01T00:00:00'
        }
        mock_get_response.return_value = mock_response
        
        response = client.get("/export/1/pdf", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'

class TestStatsEndpoints:
    """Test statistics endpoints"""
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.count_responses_by_user')
    async def test_get_user_stats(self, mock_count, mock_get_user):
        """Test getting user statistics"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock count
        mock_count.return_value = 10
        
        response = client.get("/stats", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 200
        data = response.json()
        assert 'total_responses' in data
        assert 'total_folders' in data

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        response = client.get("/folders")
        assert response.status_code == 403
    
    @patch('api_main.auth_manager.get_current_user')
    async def test_invalid_user(self, mock_get_user):
        """Test invalid user scenarios"""
        mock_get_user.return_value = None
        
        response = client.get("/folders", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401
    
    @patch('api_main.auth_manager.get_current_user')
    @patch('api_main.db.get_response_by_id')
    async def test_response_not_found(self, mock_get_response, mock_get_user):
        """Test response not found scenario"""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Mock response not found
        mock_get_response.return_value = None
        
        response = client.get("/responses/999", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__]) 