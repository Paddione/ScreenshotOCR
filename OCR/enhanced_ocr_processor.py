#!/usr/bin/env python3
"""
Enhanced OCR Processor - Advanced image processing and text extraction
Improved version with better preprocessing, multiple strategies, and quality assessment
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
import google.generativeai as genai
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class OCRStrategy:
    """Configuration for different OCR strategies"""
    name: str
    psm: int
    oem: int
    config: str
    preprocessing_type: str
    description: str

@dataclass
class ImageQualityMetrics:
    """Metrics for assessing image quality"""
    sharpness: float
    contrast: float
    brightness: float
    noise_level: float
    text_density: float
    overall_score: float

class EnhancedOCRProcessor:
    """Enhanced OCR processor with advanced preprocessing and multiple strategies"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY environment variable not set. OpenAI fallback disabled.")
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY environment variable not set. Gemini AI is disabled.")

        if not self.openai_api_key and not self.gemini_api_key:
            raise ValueError("At least one AI API key (OPENAI_API_KEY or GEMINI_API_KEY) must be set.")
            
        # Initialize OpenAI client
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        # Initialize Gemini client
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            
        # Enhanced language mapping with more languages
        self.language_codes = {
            'german': 'deu',
            'english': 'eng',
            'spanish': 'spa',
            'french': 'fra',
            'italian': 'ita',
            'portuguese': 'por',
            'dutch': 'nld',
            'auto': 'deu+eng+spa+fra',
            'multi_european': 'deu+eng+spa+fra+ita+por+nld'
        }
        
        # Multiple OCR strategies for different image types
        self.ocr_strategies = [
            OCRStrategy(
                name="document_text",
                psm=6,  # Uniform text block
                oem=3,  # Default OCR Engine Mode
                config="--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
                preprocessing_type="document",
                description="For clean document text with uniform layout"
            ),
            OCRStrategy(
                name="screenshot_mixed",
                psm=11,  # Sparse text
                oem=3,
                config="--psm 11 --oem 3",
                preprocessing_type="screenshot", 
                description="For screenshots with mixed text and graphics"
            ),
            OCRStrategy(
                name="single_line",
                psm=8,  # Single word
                oem=3,
                config="--psm 8 --oem 3",
                preprocessing_type="line",
                description="For single lines or words"
            ),
            OCRStrategy(
                name="web_content",
                psm=3,  # Fully automatic page segmentation
                oem=3,
                config="--psm 3 --oem 3",
                preprocessing_type="web",
                description="For web pages and complex layouts"
            ),
            OCRStrategy(
                name="dense_text",
                psm=6,  # Uniform text block
                oem=1,  # Legacy OCR engine
                config="--psm 6 --oem 1",
                preprocessing_type="document_enhanced",
                description="For dense text with legacy engine"
            )
        ]
    
    async def start_processing(self):
        """Start the enhanced OCR processing loop"""
        logger.info("Starting Enhanced OCR processor...")
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        
        try:
            # Test Redis connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            
            # Start processing loop
            await self.processing_loop()
            
        except Exception as e:
            logger.error(f"Error starting Enhanced OCR processor: {e}")
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
                    job = json.loads(job_json.replace("'", '"'))
                    
                    logger.info(f"Processing enhanced OCR job: {job}")
                    await self.process_job(job)
                
            except Exception as e:
                logger.error(f"Error in enhanced processing loop: {e}")
                await asyncio.sleep(5)
    
    async def process_job(self, job: Dict):
        """Process a single OCR job with enhanced pipeline"""
        try:
            file_path = job.get('file_path')
            user_id = job.get('user_id')
            folder_id = job.get('folder_id')
            
            if not file_path or not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return
            
            start_time = time.time()
            
            # Step 1: Load and assess image quality
            original_image = self.load_image(file_path)
            quality_metrics = self.assess_image_quality(original_image)
            
            logger.info(f"Image quality assessment: {quality_metrics.overall_score:.1f}%")
            
            # Step 2: Apply multiple OCR strategies
            ocr_results = await self.apply_multiple_strategies(original_image, quality_metrics)
            
            # Step 3: Select best result
            best_result = self.select_best_result(ocr_results)
            
            # Step 4: Post-process text
            enhanced_text = self.post_process_text(best_result['text'])
            best_result['text'] = enhanced_text
            
            # Step 5: Analyze with AI
            ai_analysis = await self.analyze_with_ai(best_result['text'])
            
            # Step 6: Store results with enhanced metadata
            await self.store_enhanced_results(
                user_id, 
                folder_id, 
                best_result, 
                ai_analysis, 
                file_path,
                quality_metrics,
                len(ocr_results)
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Enhanced OCR job processed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing enhanced OCR job: {e}")
    
    def load_image(self, file_path: str) -> np.ndarray:
        """Load image with error handling"""
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            return image
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise
    
    def assess_image_quality(self, image: np.ndarray) -> ImageQualityMetrics:
        """Assess image quality for OCR suitability"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate sharpness using Laplacian variance
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate contrast using standard deviation
            contrast = gray.std()
            
            # Calculate brightness using mean
            brightness = gray.mean()
            
            # Estimate noise level using high-frequency content
            noise_level = cv2.fastNlMeansDenoising(gray).var() / gray.var()
            
            # Estimate text density using edge detection
            edges = cv2.Canny(gray, 50, 150)
            text_density = np.sum(edges > 0) / edges.size
            
            # Calculate overall score (0-100)
            sharpness_score = min(sharpness / 100, 1.0) * 100
            contrast_score = min(contrast / 50, 1.0) * 100
            brightness_score = 100 - abs(brightness - 127) / 127 * 100
            noise_score = max(0, 100 - noise_level * 100)
            text_score = min(text_density * 500, 100)
            
            overall_score = (sharpness_score + contrast_score + brightness_score + noise_score + text_score) / 5
            
            return ImageQualityMetrics(
                sharpness=sharpness_score,
                contrast=contrast_score,
                brightness=brightness_score,
                noise_level=noise_score,
                text_density=text_score,
                overall_score=overall_score
            )
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return ImageQualityMetrics(50, 50, 50, 50, 50, 50)
    
    def preprocess_image(self, image: np.ndarray, preprocessing_type: str) -> np.ndarray:
        """Apply different preprocessing strategies based on image type"""
        try:
            if preprocessing_type == "document":
                return self._preprocess_document(image)
            elif preprocessing_type == "screenshot":
                return self._preprocess_screenshot(image)
            elif preprocessing_type == "web":
                return self._preprocess_web_content(image)
            elif preprocessing_type == "line":
                return self._preprocess_single_line(image)
            elif preprocessing_type == "document_enhanced":
                return self._preprocess_document_enhanced(image)
            else:
                return self._preprocess_default(image)
                
        except Exception as e:
            logger.error(f"Error in preprocessing {preprocessing_type}: {e}")
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _preprocess_document(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing optimized for clean document text"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply gentle denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Apply adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _preprocess_screenshot(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing optimized for screenshots with mixed content"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply median filter to reduce noise
        denoised = cv2.medianBlur(enhanced, 3)
        
        # Apply Otsu's thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def _preprocess_web_content(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing optimized for web pages with complex layouts"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply CLAHE with smaller tile size for web content
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
        enhanced = clahe.apply(filtered)
        
        # Apply adaptive thresholding for varied lighting
        adaptive_thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 10
        )
        
        return adaptive_thresh
    
    def _preprocess_single_line(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing optimized for single lines or words"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to smooth
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply simple binary thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply dilation to connect text components
        kernel = np.ones((2, 1), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        return dilated
    
    def _preprocess_document_enhanced(self, image: np.ndarray) -> np.ndarray:
        """Enhanced preprocessing for dense text documents"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply advanced denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=15)
        
        # Apply unsharp masking for better text clarity
        gaussian = cv2.GaussianBlur(denoised, (5, 5), 0)
        unsharp = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
        
        # Apply adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            unsharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13, 3
        )
        
        # Apply morphological operations
        kernel = np.ones((1, 2), np.uint8)
        cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _preprocess_default(self, image: np.ndarray) -> np.ndarray:
        """Default preprocessing (similar to original but improved)"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Enhanced contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Apply threshold
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Improved morphological operations
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    async def apply_multiple_strategies(self, image: np.ndarray, quality_metrics: ImageQualityMetrics) -> List[Dict]:
        """Apply multiple OCR strategies and return all results"""
        results = []
        
        # Determine which strategies to apply based on image quality
        strategies_to_use = self._select_strategies_by_quality(quality_metrics)
        
        for strategy in strategies_to_use:
            try:
                # Apply preprocessing
                processed_image = self.preprocess_image(image, strategy.preprocessing_type)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(processed_image)
                
                # Try different languages for this strategy
                for lang_name, lang_code in self.language_codes.items():
                    try:
                        # Extract text with confidence data
                        data = pytesseract.image_to_data(
                            pil_image, 
                            lang=lang_code,
                            config=strategy.config,
                            output_type=pytesseract.Output.DICT
                        )
                        
                        # Calculate confidence
                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        
                        # Extract text
                        text = pytesseract.image_to_string(
                            pil_image,
                            lang=lang_code,
                            config=strategy.config
                        ).strip()
                        
                        if text:  # Only add if text was extracted
                            results.append({
                                'text': text,
                                'confidence': avg_confidence,
                                'language': lang_name,
                                'language_code': lang_code,
                                'strategy': strategy.name,
                                'preprocessing': strategy.preprocessing_type,
                                'text_length': len(text),
                                'word_count': len(text.split())
                            })
                            
                    except Exception as e:
                        logger.warning(f"OCR failed for {strategy.name} with {lang_name}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Strategy {strategy.name} failed: {e}")
                continue
        
        return results
    
    def _select_strategies_by_quality(self, quality_metrics: ImageQualityMetrics) -> List[OCRStrategy]:
        """Select appropriate strategies based on image quality"""
        strategies = []
        
        # Always try the basic strategies
        strategies.append(self.ocr_strategies[0])  # document_text
        strategies.append(self.ocr_strategies[1])  # screenshot_mixed
        
        # Add additional strategies based on quality
        if quality_metrics.text_density > 60:
            strategies.append(self.ocr_strategies[4])  # dense_text
        
        if quality_metrics.overall_score < 60:
            strategies.append(self.ocr_strategies[3])  # web_content
        
        if quality_metrics.sharpness < 50:
            strategies.append(self.ocr_strategies[2])  # single_line
        
        return strategies
    
    def select_best_result(self, results: List[Dict]) -> Dict:
        """Select the best result from multiple OCR attempts"""
        if not results:
            return {
                'text': '',
                'confidence': 0,
                'language': 'unknown',
                'language_code': 'eng',
                'strategy': 'none',
                'preprocessing': 'none'
            }
        
        # Score each result based on multiple factors
        scored_results = []
        for result in results:
            score = self._calculate_result_score(result)
            scored_results.append((score, result))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        best_result = scored_results[0][1]
        logger.info(f"Selected best result: {best_result['strategy']} with {best_result['language']} "
                   f"(confidence: {best_result['confidence']:.1f}%, score: {scored_results[0][0]:.1f})")
        
        return best_result
    
    def _calculate_result_score(self, result: Dict) -> float:
        """Calculate a score for OCR result quality"""
        score = 0
        
        # Confidence weight (40%)
        score += result['confidence'] * 0.4
        
        # Text length weight (20%) - longer text often more reliable
        text_length_score = min(result['text_length'] / 100, 1.0) * 100
        score += text_length_score * 0.2
        
        # Word count weight (15%) - more words often better
        word_count_score = min(result['word_count'] / 10, 1.0) * 100
        score += word_count_score * 0.15
        
        # Strategy bonus (15%) - prefer certain strategies
        strategy_bonus = {
            'document_text': 10,
            'screenshot_mixed': 8,
            'web_content': 6,
            'dense_text': 7,
            'single_line': 5
        }
        score += strategy_bonus.get(result['strategy'], 0) * 0.15
        
        # Language bonus (10%) - prefer auto-detected languages
        language_bonus = {
            'auto': 5,
            'multi_european': 8,
            'english': 7,
            'german': 7
        }
        score += language_bonus.get(result['language'], 0) * 0.10
        
        return score
    
    def post_process_text(self, text: str) -> str:
        """Post-process extracted text to improve quality"""
        if not text:
            return text
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR error
        text = text.replace('0', 'O')  # In text context
        text = text.replace('5', 'S')  # In text context
        
        # Remove artifacts
        text = ''.join(char for char in text if char.isprintable())
        
        return text.strip()
    
    async def analyze_with_ai(self, text: str) -> Dict:
        """
        Analyze the extracted text with an AI model (Gemini first, then OpenAI as fallback)
        to extract structured data like invoice details, contact info, etc.
        """
        if not text.strip():
            return {"error": "No text to analyze"}

        # Try Gemini first
        if self.gemini_api_key:
            try:
                logger.info("Analyzing text with Gemini...")
                model = genai.GenerativeModel('gemini-pro')
                response = await model.generate_content_async(
                    f"Extract key information from the following OCR text. "
                    f"Format the output as a JSON object with fields for 'title', "
                    f"'summary', and 'entities' (e.g., dates, names, locations).\n\n"
                    f"Text: {text}"
                )
                
                # Assuming the response is in JSON format
                return json.loads(response.text)

            except Exception as e:
                logger.error(f"Error with Gemini AI: {e}. Falling back to OpenAI.")

        # Fallback to OpenAI
        if self.openai_api_key:
            try:
                logger.info("Analyzing text with OpenAI...")
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an intelligent assistant that extracts structured data from text."},
                        {"role": "user", "content": f"Extract key information from the following OCR text. "
                                                    f"Format the output as a JSON object with fields for 'title', "
                                                    f"'summary', and 'entities' (e.g., dates, names, locations).\n\n"
                                                    f"Text: {text}"}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                content = response['choices'][0]['message']['content']
                return json.loads(content)

            except Exception as e:
                logger.error(f"Error with OpenAI AI: {e}")
                return {"error": f"OpenAI analysis failed: {e}"}

        return {"error": "No AI provider is available or both failed."}
    
    async def store_enhanced_results(self, user_id: Optional[int], folder_id: Optional[int], 
                                   ocr_result: Dict, ai_analysis: Dict, file_path: str,
                                   quality_metrics: ImageQualityMetrics, strategies_tried: int):
        """Store results with enhanced metadata"""
        try:
            # For client uploads without user_id, use default user (admin)
            if user_id is None:
                user_id = 1
            
            # Prepare enhanced data for storage
            storage_data = {
                'user_id': user_id,
                'folder_id': folder_id,
                'ocr_text': ocr_result['text'],
                'ai_response': ai_analysis['analysis'],
                'image_path': file_path,
                'ocr_confidence': ocr_result['confidence'],
                'ocr_language': ocr_result['language'],
                'ai_model': ai_analysis['model'],
                'ai_tokens': ai_analysis['tokens_used'],
                'ocr_strategy': ocr_result['strategy'],
                'preprocessing_type': ocr_result['preprocessing'],
                'image_quality_score': quality_metrics.overall_score,
                'strategies_tried': strategies_tried,
                'text_length': len(ocr_result['text']),
                'word_count': len(ocr_result['text'].split())
            }
            
            # Add to Redis queue for database storage
            await self.redis_client.lpush("storage_queue", json.dumps(storage_data))
            
            logger.info(f"Enhanced results queued for database storage (quality: {quality_metrics.overall_score:.1f}%)")
            
        except Exception as e:
            logger.error(f"Error storing enhanced results: {e}")

async def main():
    """Main entry point"""
    processor = EnhancedOCRProcessor()
    await processor.start_processing()

if __name__ == "__main__":
    asyncio.run(main()) 