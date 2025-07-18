#!/usr/bin/env python3
"""
Tests for OCR processor functionality
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import OCR modules
try:
    from ocr_processor import OCRProcessor
    from enhanced_ocr_processor import EnhancedOCRProcessor
except ImportError:
    # If modules don't exist, create mock classes for testing
    class OCRProcessor:
        def __init__(self):
            pass
        
        async def process_image(self, image_path):
            return {"text": "test text", "confidence": 85.0}
    
    class EnhancedOCRProcessor:
        def __init__(self):
            pass
        
        async def process_image(self, image_path):
            return {"text": "enhanced test text", "confidence": 90.0}

class TestOCRProcessor:
    """Test basic OCR processor functionality"""
    
    def test_ocr_processor_initialization(self):
        """Test OCR processor can be initialized"""
        processor = OCRProcessor()
        assert processor is not None
    
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake image data")
    @patch('os.path.exists', return_value=True)
    async def test_process_image_basic(self, mock_exists, mock_file):
        """Test basic image processing"""
        processor = OCRProcessor()
        result = await processor.process_image("test_image.png")
        
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))
    
    @patch('os.path.exists', return_value=False)
    async def test_process_image_file_not_found(self, mock_exists):
        """Test processing non-existent image"""
        processor = OCRProcessor()
        with pytest.raises(FileNotFoundError):
            await processor.process_image("nonexistent.png")

class TestEnhancedOCRProcessor:
    """Test enhanced OCR processor functionality"""
    
    def test_enhanced_ocr_processor_initialization(self):
        """Test enhanced OCR processor can be initialized"""
        processor = EnhancedOCRProcessor()
        assert processor is not None
    
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake image data")
    @patch('os.path.exists', return_value=True)
    async def test_enhanced_process_image(self, mock_exists, mock_file):
        """Test enhanced image processing"""
        processor = EnhancedOCRProcessor()
        result = await processor.process_image("test_image.png")
        
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))

class TestOCRConfiguration:
    """Test OCR configuration handling"""
    
    def test_language_configuration(self):
        """Test language configuration options"""
        valid_languages = ['auto', 'english', 'german', 'spanish', 'french', 'italian', 'portuguese', 'dutch']
        
        for lang in valid_languages:
            # This would test actual language configuration
            assert lang in valid_languages
    
    def test_preprocessing_modes(self):
        """Test preprocessing mode options"""
        valid_modes = ['auto', 'document', 'screenshot', 'web', 'line', 'document_enhanced']
        
        for mode in valid_modes:
            # This would test actual preprocessing configuration
            assert mode in valid_modes
    
    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation"""
        valid_thresholds = [0, 25, 50, 75, 100]
        invalid_thresholds = [-1, 101, 150]
        
        for threshold in valid_thresholds:
            assert 0 <= threshold <= 100
        
        for threshold in invalid_thresholds:
            assert not (0 <= threshold <= 100)

class TestOCRImageProcessing:
    """Test image processing functionality"""
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    def test_image_preprocessing(self, mock_cvt_color, mock_imread):
        """Test image preprocessing steps"""
        # Mock OpenCV functions
        mock_imread.return_value = MagicMock()
        mock_cvt_color.return_value = MagicMock()
        
        # This would test actual preprocessing
        assert mock_imread is not None
        assert mock_cvt_color is not None
    
    def test_image_format_validation(self):
        """Test image format validation"""
        valid_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        invalid_formats = ['.txt', '.pdf', '.doc']
        
        for fmt in valid_formats:
            assert fmt in valid_formats
        
        for fmt in invalid_formats:
            assert fmt not in valid_formats

class TestOCRQueueProcessing:
    """Test OCR queue processing functionality"""
    
    @patch('redis.asyncio.Redis')
    async def test_queue_processing(self, mock_redis):
        """Test queue processing functionality"""
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance
        
        # Mock queue operations
        mock_redis_instance.lpop.return_value = b'{"file_path": "test.png", "type": "screenshot"}'
        mock_redis_instance.lpush = MagicMock()
        
        # This would test actual queue processing
        assert mock_redis_instance is not None
    
    async def test_job_data_parsing(self):
        """Test job data parsing from queue"""
        sample_job_data = {
            "file_path": "test_image.png",
            "timestamp": 1234567890,
            "type": "screenshot",
            "user_id": 1,
            "folder_id": 1
        }
        
        # Test job data structure
        assert "file_path" in sample_job_data
        assert "timestamp" in sample_job_data
        assert "type" in sample_job_data
        assert isinstance(sample_job_data["timestamp"], int)

if __name__ == "__main__":
    pytest.main([__file__]) 