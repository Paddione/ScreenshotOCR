#!/usr/bin/env python3
"""
Tests for text analyzer functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
import asyncio

# Import the text analyzer module
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_analyzer import TextAnalyzer

class TestTextAnalyzerInitialization:
    """Test TextAnalyzer initialization"""
    
    def test_text_analyzer_init_success(self):
        """Test successful TextAnalyzer initialization"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            analyzer = TextAnalyzer()
            
            assert analyzer.redis_url == 'redis://localhost:6379'
            assert analyzer.openai_api_key == 'test_openai_key'
    
    def test_text_analyzer_init_missing_openai_key(self):
        """Test TextAnalyzer initialization without OpenAI API key"""
        # Mock environment without OpenAI key
        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                TextAnalyzer()

class TestTextAnalyzerProcessing:
    """Test text analysis processing functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            self.analyzer = TextAnalyzer()
    
    @patch('text_analyzer.redis.from_url')
    async def test_start_processing_success(self, mock_redis_from_url):
        """Test successful processing start"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock Redis ping
        mock_redis_client.ping.return_value = True
        
        # Mock processing loop to return early
        with patch.object(self.analyzer, 'processing_loop', new_callable=AsyncMock) as mock_loop:
            mock_loop.side_effect = Exception("Test exit")
            
            # Test processing start
            with pytest.raises(Exception, match="Test exit"):
                await self.analyzer.start_processing()
            
            # Verify Redis connection
            mock_redis_from_url.assert_called_once_with(
                'redis://localhost:6379', 
                encoding="utf-8", 
                decode_responses=True
            )
            mock_redis_client.ping.assert_called_once()
    
    @patch('text_analyzer.redis.from_url')
    async def test_start_processing_redis_error(self, mock_redis_from_url):
        """Test processing start with Redis error"""
        # Mock Redis client with error
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock Redis ping to fail
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        
        # Test processing start
        with pytest.raises(Exception, match="Redis connection failed"):
            await self.analyzer.start_processing()
    
    @patch('text_analyzer.redis.from_url')
    async def test_processing_loop_with_job(self, mock_redis_from_url):
        """Test processing loop with job data"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock job data
        job_data = {
            'direct_text': 'Test text content',
            'user_id': 1,
            'folder_id': 1,
            'language': 'auto'
        }
        mock_redis_client.brpop.return_value = ('text_analysis_queue', json.dumps(job_data))
        
        # Mock process_text_job
        with patch.object(self.analyzer, 'process_text_job', new_callable=AsyncMock) as mock_process:
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                ('text_analysis_queue', json.dumps(job_data)),
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.analyzer.processing_loop()
            
            # Verify job processing
            mock_process.assert_called_once_with(job_data)
    
    @patch('text_analyzer.redis.from_url')
    async def test_processing_loop_no_job(self, mock_redis_from_url):
        """Test processing loop with no job data"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock no job data (timeout)
        mock_redis_client.brpop.return_value = None
        
        # Mock process_text_job
        with patch.object(self.analyzer, 'process_text_job', new_callable=AsyncMock) as mock_process:
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                None,
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.analyzer.processing_loop()
            
            # Verify no job processing
            mock_process.assert_not_called()
    
    @patch('text_analyzer.redis.from_url')
    async def test_processing_loop_invalid_json(self, mock_redis_from_url):
        """Test processing loop with invalid JSON"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock invalid JSON data
        mock_redis_client.brpop.return_value = ('text_analysis_queue', 'invalid json')
        
        # Mock process_text_job
        with patch.object(self.analyzer, 'process_text_job', new_callable=AsyncMock) as mock_process:
            # Set up loop to run once then exit
            mock_redis_client.brpop.side_effect = [
                ('text_analysis_queue', 'invalid json'),
                Exception("Test exit")
            ]
            
            # Test processing loop
            with pytest.raises(Exception, match="Test exit"):
                await self.analyzer.processing_loop()
            
            # Verify no job processing due to JSON error
            mock_process.assert_not_called()

class TestTextJobProcessing:
    """Test individual text job processing"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            self.analyzer = TextAnalyzer()
    
    @patch('text_analyzer.redis.from_url')
    @patch('text_analyzer.openai.ChatCompletion.create')
    async def test_process_text_job_success(self, mock_openai_create, mock_redis_from_url):
        """Test successful text job processing"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "AI analysis result"
        mock_response.usage.total_tokens = 150
        mock_openai_create.return_value = mock_response
        
        # Mock store_text_analysis_results
        with patch.object(self.analyzer, 'store_text_analysis_results', new_callable=AsyncMock) as mock_store:
            # Test job processing
            job_data = {
                'direct_text': 'Test text content',
                'user_id': 1,
                'folder_id': 1,
                'language': 'auto',
                'file_path': '/path/to/file.txt'
            }
            
            await self.analyzer.process_text_job(job_data)
            
            # Verify OpenAI call
            mock_openai_create.assert_called_once()
            call_args = mock_openai_create.call_args
            assert call_args[1]['model'] == 'gpt-4'
            assert call_args[1]['max_tokens'] == 1500
            assert call_args[1]['temperature'] == 0.7
            
            # Verify storage call
            mock_store.assert_called_once_with(
                1, 1, 'Test text content', 
                {'analysis': 'AI analysis result', 'model': 'gpt-4', 'tokens_used': 150},
                '/path/to/file.txt', 'auto'
            )
    
    @patch('text_analyzer.redis.from_url')
    async def test_process_text_job_empty_text(self, mock_redis_from_url):
        """Test text job processing with empty text"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock store_text_analysis_results
        with patch.object(self.analyzer, 'store_text_analysis_results', new_callable=AsyncMock) as mock_store:
            # Test job processing with empty text
            job_data = {
                'direct_text': '',
                'user_id': 1,
                'folder_id': 1,
                'language': 'auto'
            }
            
            await self.analyzer.process_text_job(job_data)
            
            # Verify no storage call for empty text
            mock_store.assert_not_called()
    
    @patch('text_analyzer.redis.from_url')
    @patch('text_analyzer.openai.ChatCompletion.create')
    async def test_process_text_job_openai_error(self, mock_openai_create, mock_redis_from_url):
        """Test text job processing with OpenAI error"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Mock OpenAI error
        mock_openai_create.side_effect = Exception("OpenAI API error")
        
        # Mock store_text_analysis_results
        with patch.object(self.analyzer, 'store_text_analysis_results', new_callable=AsyncMock) as mock_store:
            # Test job processing
            job_data = {
                'direct_text': 'Test text content',
                'user_id': 1,
                'folder_id': 1,
                'language': 'auto'
            }
            
            await self.analyzer.process_text_job(job_data)
            
            # Verify storage call with error response
            mock_store.assert_called_once()
            call_args = mock_store.call_args[0]
            assert 'Error occurred during AI analysis' in call_args[3]['analysis']
            assert call_args[3]['model'] == 'error'
            assert call_args[3]['tokens_used'] == 0

class TestAIAnalysis:
    """Test AI analysis functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            self.analyzer = TextAnalyzer()
    
    @patch('text_analyzer.openai.ChatCompletion.create')
    async def test_analyze_text_with_ai_success(self, mock_openai_create):
        """Test successful AI text analysis"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is an email from John Doe regarding project updates."
        mock_response.usage.total_tokens = 200
        mock_openai_create.return_value = mock_response
        
        # Test AI analysis
        result = await self.analyzer.analyze_text_with_ai("Test email content", "auto")
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'analysis' in result
        assert 'model' in result
        assert 'tokens_used' in result
        assert result['analysis'] == "This is an email from John Doe regarding project updates."
        assert result['model'] == 'gpt-4'
        assert result['tokens_used'] == 200
        
        # Verify OpenAI call
        mock_openai_create.assert_called_once()
        call_args = mock_openai_create.call_args
        assert call_args[1]['model'] == 'gpt-4'
        assert call_args[1]['max_tokens'] == 1500
        assert call_args[1]['temperature'] == 0.7
        
        # Verify prompt content
        messages = call_args[1]['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert 'Test email content' in messages[1]['content']
    
    async def test_analyze_text_with_ai_empty_text(self):
        """Test AI analysis with empty text"""
        # Test AI analysis with empty text
        result = await self.analyzer.analyze_text_with_ai("", "auto")
        
        # Verify result for empty text
        assert isinstance(result, dict)
        assert result['analysis'] == 'No text provided for analysis.'
        assert result['model'] == 'none'
        assert result['tokens_used'] == 0
    
    async def test_analyze_text_with_ai_whitespace_only(self):
        """Test AI analysis with whitespace-only text"""
        # Test AI analysis with whitespace
        result = await self.analyzer.analyze_text_with_ai("   \n\t   ", "auto")
        
        # Verify result for whitespace text
        assert isinstance(result, dict)
        assert result['analysis'] == 'No text provided for analysis.'
        assert result['model'] == 'none'
        assert result['tokens_used'] == 0
    
    @patch('text_analyzer.openai.ChatCompletion.create')
    async def test_analyze_text_with_ai_error(self, mock_openai_create):
        """Test AI analysis with error"""
        # Mock OpenAI error
        mock_openai_create.side_effect = Exception("API rate limit exceeded")
        
        # Test AI analysis
        result = await self.analyzer.analyze_text_with_ai("Test content", "auto")
        
        # Verify error result
        assert isinstance(result, dict)
        assert 'Error occurred during AI analysis' in result['analysis']
        assert result['model'] == 'error'
        assert result['tokens_used'] == 0

class TestStorageOperations:
    """Test storage operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6379',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            self.analyzer = TextAnalyzer()
    
    @patch('text_analyzer.redis.from_url')
    async def test_store_text_analysis_results(self, mock_redis_from_url):
        """Test storing text analysis results"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Test storage
        ai_analysis = {
            'analysis': 'AI analysis result',
            'model': 'gpt-4',
            'tokens_used': 150
        }
        
        await self.analyzer.store_text_analysis_results(
            1, 1, 'Test text content', ai_analysis, '/path/to/file.txt', 'auto'
        )
        
        # Verify Redis call
        mock_redis_client.lpush.assert_called_once()
        call_args = mock_redis_client.lpush.call_args
        assert call_args[0][0] == 'storage_queue'
        
        # Verify stored data
        stored_data = json.loads(call_args[0][1])
        assert stored_data['user_id'] == 1
        assert stored_data['folder_id'] == 1
        assert stored_data['ocr_text'] == 'Test text content'
        assert stored_data['ai_response'] == 'AI analysis result'
        assert stored_data['image_path'] == '/path/to/file.txt'
        assert stored_data['ocr_confidence'] == 100.0
        assert stored_data['ocr_language'] == 'auto'
        assert stored_data['ai_model'] == 'gpt-4'
        assert stored_data['ai_tokens'] == 150
        assert stored_data['ocr_strategy'] == 'clipboard_text'
        assert stored_data['preprocessing_type'] == 'none'
        assert stored_data['image_quality_score'] == 100.0
        assert stored_data['strategies_tried'] == 1
        assert stored_data['text_length'] == 18
        assert stored_data['word_count'] == 3
    
    @patch('text_analyzer.redis.from_url')
    async def test_store_text_analysis_results_no_user_id(self, mock_redis_from_url):
        """Test storing text analysis results without user ID"""
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_from_url.return_value = mock_redis_client
        
        # Test storage without user ID
        ai_analysis = {
            'analysis': 'AI analysis result',
            'model': 'gpt-4',
            'tokens_used': 150
        }
        
        await self.analyzer.store_text_analysis_results(
            None, 1, 'Test text content', ai_analysis, '/path/to/file.txt', 'auto'
        )
        
        # Verify Redis call with default user ID
        mock_redis_client.lpush.assert_called_once()
        call_args = mock_redis_client.lpush.call_args
        stored_data = json.loads(call_args[0][1])
        assert stored_data['user_id'] == 1  # Default user ID

if __name__ == "__main__":
    pytest.main([__file__]) 