#!/usr/bin/env python3
"""
Storage Processor - Handles database storage operations from Redis queue
"""

import os
import json
import asyncio
import logging
import redis.asyncio as redis
from api_database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StorageProcessor:
    """Handles storage operations from Redis queue"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    async def start_processing(self):
        """Start the storage processing loop"""
        logger.info("Starting storage processor...")
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        
        # Connect to Database
        self.db = Database()
        await self.db.connect()
        
        try:
            # Test connections
            await self.redis_client.ping()
            await self.db.execute("SELECT 1")
            logger.info("Connected to Redis and Database successfully")
            
            # Start processing loop
            await self.processing_loop()
            
        except Exception as e:
            logger.error(f"Error starting storage processor: {e}")
            raise
        finally:
            if hasattr(self, 'redis_client'):
                await self.redis_client.close()
            if hasattr(self, 'db'):
                await self.db.disconnect()
    
    async def processing_loop(self):
        """Main processing loop"""
        while True:
            try:
                # Get job from storage queue (blocking with timeout)
                job_data = await self.redis_client.brpop("storage_queue", timeout=30)
                
                if job_data:
                    queue_name, job_json = job_data
                    
                    try:
                        # Parse job data
                        job = json.loads(job_json)
                        logger.info(f"Processing storage job for user {job.get('user_id')}")
                        
                        await self.store_response(job)
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in storage queue: {e}")
                    except Exception as e:
                        logger.error(f"Error processing storage job: {e}")
                
            except Exception as e:
                logger.error(f"Error in storage processing loop: {e}")
                await asyncio.sleep(5)
    
    async def store_response(self, job_data):
        """Store OCR response in database"""
        try:
            user_id = job_data.get('user_id')
            folder_id = job_data.get('folder_id')
            ocr_text = job_data.get('ocr_text', '')
            ai_response = job_data.get('ai_response', '')
            image_path = job_data.get('image_path', '')
            ocr_confidence = job_data.get('ocr_confidence', 0)
            ocr_language = job_data.get('ocr_language', 'unknown')
            ai_model = job_data.get('ai_model', 'unknown')
            ai_tokens = job_data.get('ai_tokens', 0)
            
            # Validate required fields
            if not user_id:
                logger.error("Missing user_id in storage job")
                return
            
            # Insert into database
            query = """
                INSERT INTO responses (
                    user_id, folder_id, ocr_text, ai_response, image_path,
                    ocr_confidence, ocr_language, ai_model, ai_tokens
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """
            
            response_id = await self.db.fetchval(
                query,
                user_id, folder_id, ocr_text, ai_response, image_path,
                ocr_confidence, ocr_language, ai_model, ai_tokens
            )
            
            logger.info(f"Stored response with ID {response_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing response: {e}")
            # Optionally, could re-queue the job for retry
            raise

async def main():
    """Main entry point"""
    processor = StorageProcessor()
    await processor.start_processing()

if __name__ == "__main__":
    asyncio.run(main()) 