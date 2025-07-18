#!/usr/bin/env python3
"""
Text Analysis Processor - Direct AI analysis for clipboard text
Handles text content that bypasses OCR processing
"""

import os
import json
import time
import logging
import asyncio
import openai
import redis.asyncio as redis
from typing import Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TextAnalyzer:
    """Text analysis processor for clipboard content"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
    
    async def start_processing(self):
        """Start the text analysis processing loop"""
        logger.info("Starting Text Analysis processor...")
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        
        try:
            # Test Redis connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            
            # Start processing loop
            await self.processing_loop()
            
        except Exception as e:
            logger.error(f"Error starting Text Analysis processor: {e}")
            raise
        finally:
            if hasattr(self, 'redis_client'):
                await self.redis_client.close()
    
    async def processing_loop(self):
        """Main processing loop"""
        while True:
            try:
                # Get job from text analysis queue
                job_data = await self.redis_client.brpop("text_analysis_queue", timeout=30)
                
                if job_data:
                    queue_name, job_json = job_data
                    job = json.loads(job_json.replace("'", '"'))
                    
                    logger.info(f"Processing text analysis job: {job}")
                    await self.process_text_job(job)
                
            except Exception as e:
                logger.error(f"Error in text analysis processing loop: {e}")
                await asyncio.sleep(5)
    
    async def process_text_job(self, job: Dict):
        """Process a text analysis job"""
        try:
            text_content = job.get('direct_text', '')
            user_id = job.get('user_id')
            folder_id = job.get('folder_id')
            language = job.get('language', 'auto')
            
            if not text_content.strip():
                logger.error("Empty text content received")
                return
            
            start_time = time.time()
            
            # Analyze text with AI
            ai_analysis = await self.analyze_text_with_ai(text_content, language)
            
            # Store results
            await self.store_text_analysis_results(
                user_id,
                folder_id,
                text_content,
                ai_analysis,
                job.get('file_path', ''),
                language
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Text analysis completed in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing text analysis job: {e}")
    
    async def analyze_text_with_ai(self, text: str, language: str = 'auto') -> Dict:
        """Analyze text with OpenAI"""
        try:
            if not text.strip():
                return {
                    'analysis': 'No text provided for analysis.',
                    'model': 'none',
                    'tokens_used': 0
                }
            
            # Enhanced prompt for text analysis
            prompt = f"""
Please analyze the following text content that was pasted from clipboard:

{text}

Provide a comprehensive analysis that includes:
1. Content type identification (email, document, code, webpage content, notes, etc.)
2. Key information extraction and important points
3. Context and purpose assessment
4. Structure and formatting analysis
5. Any actionable items, tasks, or next steps
6. Quality assessment and suggestions for improvement
7. Summary of the main content
8. If it's code: language detection, functionality overview, and potential issues
9. If it's an email: sender, subject, key points, and required actions
10. If it's a document: main topics, conclusions, and recommendations

Please respond in the same language as the input text when possible, or in English if the language is unclear.
"""

            # Call OpenAI API
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert assistant that analyzes text content from clipboard and provides detailed, useful insights. You excel at understanding context, extracting key information, and providing actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            logger.info(f"Text AI analysis completed: {tokens_used} tokens used")
            
            return {
                'analysis': analysis,
                'model': 'gpt-3.5-turbo',
                'tokens_used': tokens_used
            }
            
        except Exception as e:
            logger.error(f"Error with text AI analysis: {e}")
            return {
                'analysis': f'Error occurred during AI analysis: {str(e)}',
                'model': 'error',
                'tokens_used': 0
            }
    
    async def store_text_analysis_results(self, user_id: Optional[int], folder_id: Optional[int], 
                                         text_content: str, ai_analysis: Dict, file_path: str, language: str):
        """Store text analysis results"""
        try:
            # For client uploads without user_id, use default user (admin)
            if user_id is None:
                user_id = 1
            
            # Prepare data for storage
            storage_data = {
                'user_id': user_id,
                'folder_id': folder_id,
                'ocr_text': text_content,
                'ai_response': ai_analysis['analysis'],
                'image_path': file_path,
                'ocr_confidence': 100.0,  # Direct text has 100% confidence
                'ocr_language': language,
                'ai_model': ai_analysis['model'],
                'ai_tokens': ai_analysis['tokens_used'],
                'ocr_strategy': 'clipboard_text',
                'preprocessing_type': 'none',
                'image_quality_score': 100.0,
                'strategies_tried': 1,
                'text_length': len(text_content),
                'word_count': len(text_content.split())
            }
            
            # Add to Redis queue for database storage
            await self.redis_client.lpush("storage_queue", json.dumps(storage_data))
            
            logger.info(f"Text analysis results queued for database storage ({len(text_content)} chars)")
            
        except Exception as e:
            logger.error(f"Error storing text analysis results: {e}")

async def main():
    """Main entry point"""
    analyzer = TextAnalyzer()
    await analyzer.start_processing()

if __name__ == "__main__":
    asyncio.run(main()) 