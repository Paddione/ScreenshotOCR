#!/usr/bin/env python3
"""
Tests for API main functionality
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json

# Set environment variables for testing
os.environ['API_AUTH_TOKEN'] = '8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df'

# Import the app from api_main
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_main import app

client = TestClient(app)

# Get API token from environment
API_TOKEN = os.getenv('API_AUTH_TOKEN', '8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df')

# Common headers for authenticated requests
auth_headers = {"Authorization": f"Bearer {API_TOKEN}"}

class TestAPIHealth:
    """Test health check endpoints"""
    
    @patch('api_main.db')
    @patch('api_main.redis_client')
    def test_health_check(self, mock_redis, mock_db):
        """Test the health check endpoint"""
        # Mock database and Redis with async mocks
        mock_db.execute = AsyncMock()
        mock_redis.ping = AsyncMock()
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_info_endpoint(self):
        """Test the info endpoint"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "name" in data

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        response = client.post("/auth/login", json={})
        assert response.status_code == 422
    
    def test_register_missing_data(self):
        """Test register with missing data"""
        response = client.post("/auth/register", json={})
        assert response.status_code == 422

class TestScreenshotUpload:
    """Test screenshot upload functionality"""
    
    @patch('api_main.redis_client')
    def test_screenshot_upload_no_file(self, mock_redis):
        """Test screenshot upload without file"""
        mock_redis.lpush = AsyncMock()
        response = client.post("/screenshot", headers=auth_headers)
        assert response.status_code == 422
    
    @patch('api_main.redis_client')
    def test_screenshot_upload_invalid_file(self, mock_redis):
        """Test screenshot upload with invalid file"""
        mock_redis.lpush = AsyncMock()
        files = {"image": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/screenshot", files=files, headers=auth_headers)
        assert response.status_code == 400

class TestClipboardEndpoints:
    """Test clipboard text and image endpoints"""
    
    @patch('api_main.redis_client')
    def test_clipboard_text_no_data(self, mock_redis):
        """Test clipboard text without data"""
        mock_redis.lpush = AsyncMock()
        response = client.post("/clipboard/text", headers=auth_headers)
        assert response.status_code == 422
    
    @patch('api_main.redis_client')
    def test_clipboard_image_no_file(self, mock_redis):
        """Test clipboard image without file"""
        mock_redis.lpush = AsyncMock()
        response = client.post("/clipboard/image", headers=auth_headers)
        assert response.status_code == 422

class TestBatchUpload:
    """Test batch upload functionality"""
    
    @patch('api_main.redis_client')
    def test_batch_upload_no_files(self, mock_redis):
        """Test batch upload without files"""
        mock_redis.lpush = AsyncMock()
        response = client.post("/batch/upload", headers=auth_headers)
        assert response.status_code == 422
    
    @patch('api_main.redis_client')
    def test_batch_upload_too_many_files(self, mock_redis):
        """Test batch upload with too many files"""
        mock_redis.lpush = AsyncMock()
        files = [("images", ("test.png", b"fake image", "image/png"))] * 21
        response = client.post("/batch/upload", files=files, headers=auth_headers)
        assert response.status_code == 400

class TestOCRConfiguration:
    """Test OCR configuration endpoints"""
    
    @patch('api_main.redis_client')
    def test_ocr_config_update(self, mock_redis):
        """Test OCR configuration update"""
        mock_redis.set = AsyncMock()
        data = {
            "languages": ["english", "german"],
            "confidence_threshold": 75.0,
            "preprocessing_mode": "auto"
        }
        response = client.post("/config/ocr", data=data, headers=auth_headers)
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data
        assert response_data["message"] == "OCR configuration updated"
    
    @patch('api_main.redis_client')
    def test_ocr_config_invalid_language(self, mock_redis):
        """Test OCR configuration with invalid language"""
        mock_redis.set = AsyncMock()
        data = {
            "languages": ["invalid_language"],
            "confidence_threshold": 75.0,
            "preprocessing_mode": "auto"
        }
        response = client.post("/config/ocr", data=data, headers=auth_headers)
        assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__]) 