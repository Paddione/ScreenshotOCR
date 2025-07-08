#!/usr/bin/env python3
"""
OCR Processor - Handles image processing and text extraction
"""

import os
import json
import time
import logging
import asyncio
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import redis.asyncio as redis
import openai
from typing import Dict, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing and AI analysis"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize OpenAI client
        openai.api_key = self.openai_api_key
        
        # Configure Tesseract
        self.tesseract_config = '--oem 3 --psm 6'
        
        # Language mapping
        self.language_codes = {
            'german': 'deu',
            'english': 'eng',
            'auto': 'deu+eng'
        }
    
    async def start_processing(self):
        """Start the OCR processing loop"""
        logger.info("Starting OCR processor...")
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        
        try:
            # Test Redis connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            
            # Start processing loop
            await self.processing_loop()
            
        except Exception as e:
            logger.error(f"Error starting OCR processor: {e}")
            raise
        finally:
            if hasattr(self, 'redis_client'):
                await self.redis_client.close()
    
    async def processing_loop(self):
        """Main processing loop"""
        while True:
            try:
                # Get job from queue (blocking with timeout)
                job_data = await self.redis_client.brpop("ocr_queue", timeout=30)
                
                if job_data:
                    queue_name, job_json = job_data
                    job = json.loads(job_json.replace("'", '"'))  # Handle Python dict string
                    
                    logger.info(f"Processing job: {job}")
                    await self.process_job(job)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)
    
    async def process_job(self, job: Dict):
        """Process a single OCR job"""
        try:
            file_path = job.get('file_path')
            user_id = job.get('user_id')
            folder_id = job.get('folder_id')
            
            if not file_path or not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return
            
            start_time = time.time()
            
            # Step 1: Preprocess image
            processed_image = self.preprocess_image(file_path)
            
            # Step 2: Extract text with OCR
            ocr_result = self.extract_text(processed_image)
            
            # Step 3: Analyze with AI
            ai_analysis = await self.analyze_with_ai(ocr_result['text'])
            
            # Step 4: Store results
            await self.store_results(
                user_id, 
                folder_id, 
                ocr_result, 
                ai_analysis, 
                file_path
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Job processed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing job: {e}")
    
    def preprocess_image(self, file_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Apply threshold to get better black and white image
            _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Fallback to original image
            return cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    
    def extract_text(self, image: np.ndarray) -> Dict:
        """Extract text from preprocessed image"""
        try:
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)
            
            # Try different language combinations
            best_result = None
            best_confidence = 0
            
            for lang_name, lang_code in self.language_codes.items():
                try:
                    # Extract text with confidence data
                    data = pytesseract.image_to_data(
                        pil_image, 
                        lang=lang_code,
                        config=self.tesseract_config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Extract text
                    text = pytesseract.image_to_string(
                        pil_image,
                        lang=lang_code,
                        config=self.tesseract_config
                    ).strip()
                    
                    if avg_confidence > best_confidence and text:
                        best_result = {
                            'text': text,
                            'confidence': avg_confidence,
                            'language': lang_name,
                            'language_code': lang_code
                        }
                        best_confidence = avg_confidence
                        
                except Exception as e:
                    logger.warning(f"OCR failed for language {lang_name}: {e}")
                    continue
            
            if not best_result:
                # Fallback with default settings
                text = pytesseract.image_to_string(pil_image)
                best_result = {
                    'text': text,
                    'confidence': 0,
                    'language': 'unknown',
                    'language_code': 'eng'
                }
            
            logger.info(f"OCR completed: {len(best_result['text'])} chars, "
                       f"{best_result['confidence']:.1f}% confidence, "
                       f"language: {best_result['language']}")
            
            return best_result
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {
                'text': '',
                'confidence': 0,
                'language': 'error',
                'language_code': 'eng'
            }
    
    async def analyze_with_ai(self, text: str) -> Dict:
        """Analyze extracted text with OpenAI"""
        try:
            if not text.strip():
                return {
                    'analysis': 'No text was extracted from the image.',
                    'model': 'none',
                    'tokens_used': 0
                }
            
            # Prepare prompt
            prompt = f"""
Please analyze the following text that was extracted from a screenshot:

{text}

Provide a helpful analysis that includes:
1. What type of content this appears to be (document, webpage, application, etc.)
2. Key information or important points
3. Any actionable items or next steps
4. Summary of the main content

Please respond in the same language as the extracted text when possible.
"""

            # Call OpenAI API
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes screenshot content and provides useful insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            logger.info(f"AI analysis completed: {tokens_used} tokens used")
            
            return {
                'analysis': analysis,
                'model': 'gpt-4',
                'tokens_used': tokens_used
            }
            
        except Exception as e:
            logger.error(f"Error with AI analysis: {e}")
            return {
                'analysis': f'Error occurred during AI analysis: {str(e)}',
                'model': 'error',
                'tokens_used': 0
            }
    
    async def store_results(self, user_id: Optional[int], folder_id: Optional[int], 
                          ocr_result: Dict, ai_analysis: Dict, file_path: str):
        """Store results in database"""
        try:
            # For client uploads without user_id, use default user (admin)
            if user_id is None:
                user_id = 1  # Default to admin user
            
            # Prepare data for storage
            storage_data = {
                'user_id': user_id,
                'folder_id': folder_id,
                'ocr_text': ocr_result['text'],
                'ai_response': ai_analysis['analysis'],
                'image_path': file_path,
                'ocr_confidence': ocr_result['confidence'],
                'ocr_language': ocr_result['language'],
                'ai_model': ai_analysis['model'],
                'ai_tokens': ai_analysis['tokens_used']
            }
            
            # Add to Redis queue for database storage
            await self.redis_client.lpush("storage_queue", json.dumps(storage_data))
            
            logger.info("Results queued for database storage")
            
        except Exception as e:
            logger.error(f"Error storing results: {e}")

# OCR Processor requirements
ocr_requirements = """
pytesseract==0.3.10
opencv-python==4.8.1.78
Pillow==10.0.0
redis==5.0.1
openai==1.3.7
numpy==1.24.3
"""

async def main():
    """Main entry point"""
    processor = OCRProcessor()
    await processor.start_processing()

if __name__ == "__main__":
    asyncio.run(main())