#!/usr/bin/env python3
"""
OCR Processor Entry Point
Main entry point for the OCR processing service
"""

import asyncio
import logging
import signal
import sys
from ocr_processor import OCRProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessorService:
    """OCR Processor Service Manager"""
    
    def __init__(self):
        self.processor = None
        self.running = False
    
    async def start(self):
        """Start the OCR processor service"""
        try:
            logger.info("Starting OCR Processor Service...")
            
            # Initialize processor
            self.processor = OCRProcessor()
            self.running = True
            
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Start processing
            await self.processor.start_processing()
            
        except Exception as e:
            logger.error(f"Failed to start OCR processor: {e}")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        asyncio.create_task(self.shutdown())
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down OCR processor...")
        if self.processor:
            # Close any open connections
            if hasattr(self.processor, 'redis_client'):
                await self.processor.redis_client.close()
        
        logger.info("OCR processor shutdown complete")
        sys.exit(0)

async def main():
    """Main entry point"""
    service = ProcessorService()
    await service.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1) 