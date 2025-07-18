#!/usr/bin/env python3
"""
Screenshot-to-AI Analysis System - API Server
FastAPI application for handling screenshots and AI analysis
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn

from api_database import Database
from api_auth import AuthManager
from api_routes import router
from api_models import UserCreate, UserLogin
import redis.asyncio as redis
from datetime import datetime
import json
from typing import List
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
db = None
auth_manager = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global db, auth_manager, redis_client
    
    # Startup
    logger.info("Starting up API server...")
    
    # Initialize database
    db = Database()
    await db.connect()
    await db.create_tables()
    
    # Initialize Redis
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    
    # Initialize auth manager
    auth_manager = AuthManager(db)
    
    # Create default admin user if not exists
    await create_default_users()
    
    logger.info("API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server...")
    if db:
        await db.disconnect()
    if redis_client:
        await redis_client.close()

async def create_default_users():
    """Create default users if they don't exist"""
    try:
        # Create default admin user
        admin_exists = await db.get_user_by_username("admin")
        if not admin_exists:
            admin_user = UserCreate(
                username="admin",
                password="admin123"  # Change this in production!
            )
            await auth_manager.create_user(admin_user)
            logger.info("Default admin user created (username: admin, password: admin123)")
        
        # Create default patrick user
        patrick_exists = await db.get_user_by_username("patrick")
        if not patrick_exists:
            patrick_user = UserCreate(
                username="patrick",
                password="1170591pk"
            )
            await auth_manager.create_user(patrick_user)
            logger.info("Default patrick user created (username: patrick, password: 1170591pk)")
            
    except Exception as e:
        logger.error(f"Error creating default users: {e}")

# Create FastAPI app
app = FastAPI(
    title="Screenshot AI Analysis API",
    description="API for screenshot capture and AI analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        user = await auth_manager.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user, but make it optional for some endpoints"""
    try:
        token = credentials.credentials
        user = await auth_manager.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token for client requests"""
    try:
        token = credentials.credentials
        api_token = os.getenv('API_AUTH_TOKEN')
        
        if not api_token:
            raise HTTPException(status_code=500, detail="API token not configured")
        
        if token != api_token:
            raise HTTPException(status_code=401, detail="Invalid API token")
        
        return True
    except Exception as e:
        logger.error(f"API token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid API token")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await db.execute("SELECT 1")
        
        # Check Redis connection
        await redis_client.ping()
        
        return {"status": "healthy", "message": "All services operational"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Info endpoint
@app.get("/info")
async def get_info():
    """Get server information"""
    return {
        "name": "Screenshot AI Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(user_data: UserLogin):
    """User login"""
    try:
        token = await auth_manager.authenticate_user(user_data.username, user_data.password)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/register")
async def register(user_data: UserCreate):
    """User registration - now open to public"""
    try:
        user = await auth_manager.create_user(user_data)
        return {"message": "User created successfully", "user_id": user.id}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/refresh")
async def refresh_token(current_user = Depends(get_current_user)):
    """Refresh access token"""
    try:
        # Create new token with same user data plus current timestamp to ensure uniqueness
        import time
        token_data = {
            "sub": str(current_user.id),
            "username": current_user.username,
            "iat": int(time.time())  # Add issued-at time to make token unique
        }
        new_token = auth_manager.create_access_token(token_data)
        
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat()
    }

# Screenshot upload endpoint
@app.post("/screenshot")
async def upload_screenshot(
    image: UploadFile = File(...),
    timestamp: int = Form(None),
    _: bool = Depends(verify_api_token)
):
    """Upload screenshot for AI analysis"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = f"{upload_dir}/{image.filename}"
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Queue for OCR processing
        job_data = {
            "file_path": file_path,
            "timestamp": timestamp,
            "type": "screenshot"
        }
        
        # Add to Redis queue
        await redis_client.lpush("ocr_queue", str(job_data))
        
        logger.info(f"Screenshot queued for processing: {file_path}")
        
        return {"message": "Screenshot uploaded and queued for processing", "status": "queued"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screenshot upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# New clipboard endpoints
@app.post("/clipboard/text")
async def post_clipboard_text(
    text: str = Form(...),
    language: str = Form("auto"),
    timestamp: int = Form(None),
    user_id: int = Form(None),
    folder_id: int = Form(None),
    _: bool = Depends(verify_api_token)
):
    """Post clipboard text for AI analysis"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 100000:  # 100KB limit
            raise HTTPException(status_code=400, detail="Text too long (max 100KB)")
        
        # Create a text file for processing
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clipboard_text_{timestamp_str}.txt"
        file_path = f"{upload_dir}/{filename}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        # Queue for direct AI analysis (skip OCR)
        job_data = {
            "file_path": file_path,
            "timestamp": timestamp,
            "type": "clipboard_text",
            "user_id": user_id,
            "folder_id": folder_id,
            "language": language,
            "direct_text": text
        }
        
        # Add to Redis queue
        await redis_client.lpush("text_analysis_queue", json.dumps(job_data))
        
        logger.info(f"Clipboard text queued for analysis: {len(text)} characters")
        
        return {"message": "Clipboard text queued for analysis", "status": "queued", "text_length": len(text)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clipboard text error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/clipboard/image")
async def post_clipboard_image(
    image: UploadFile = File(...),
    timestamp: int = Form(None),
    user_id: int = Form(None),
    folder_id: int = Form(None),
    _: bool = Depends(verify_api_token)
):
    """Post clipboard image for OCR and AI analysis"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clipboard_image_{timestamp_str}.png"
        file_path = f"{upload_dir}/{filename}"
        
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Queue for OCR processing
        job_data = {
            "file_path": file_path,
            "timestamp": timestamp,
            "type": "clipboard_image",
            "user_id": user_id,
            "folder_id": folder_id
        }
        
        # Add to Redis queue
        await redis_client.lpush("ocr_queue", json.dumps(job_data))
        
        logger.info(f"Clipboard image queued for processing: {file_path}")
        
        return {"message": "Clipboard image queued for processing", "status": "queued"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clipboard image error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/batch/upload")
async def batch_upload(
    images: List[UploadFile] = File(...),
    folder_id: int = Form(None),
    batch_name: str = Form(None),
    _: bool = Depends(verify_api_token)
):
    """Batch upload multiple images for processing"""
    try:
        if len(images) > 20:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 20 files per batch")
        
        # Validate all files are images
        for image in images:
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {image.filename} is not an image")
        
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        uploaded_files = []
        
        for i, image in enumerate(images):
            filename = f"batch_{batch_id}_{i:03d}_{image.filename}"
            file_path = f"{upload_dir}/{filename}"
            
            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            
            # Queue for OCR processing
            job_data = {
                "file_path": file_path,
                "timestamp": int(time.time()),
                "type": "batch_upload",
                "batch_id": batch_id,
                "batch_name": batch_name,
                "folder_id": folder_id,
                "batch_index": i,
                "batch_total": len(images)
            }
            
            # Add to Redis queue
            await redis_client.lpush("ocr_queue", json.dumps(job_data))
            uploaded_files.append(filename)
        
        logger.info(f"Batch upload queued: {len(images)} files in batch {batch_id}")
        
        return {
            "message": f"Batch upload queued: {len(images)} files", 
            "status": "queued",
            "batch_id": batch_id,
            "files_count": len(images),
            "uploaded_files": uploaded_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced configuration endpoint
@app.post("/config/ocr")
async def update_ocr_config(
    languages: List[str] = Form(['auto']),
    confidence_threshold: float = Form(50.0),
    preprocessing_mode: str = Form('auto'),
    _: bool = Depends(verify_api_token)
):
    """Update OCR configuration settings"""
    try:
        valid_languages = ['auto', 'english', 'german', 'spanish', 'french', 'italian', 'portuguese', 'dutch']
        valid_preprocessing = ['auto', 'document', 'screenshot', 'web', 'line', 'document_enhanced']
        
        # Validate languages
        for lang in languages:
            if lang not in valid_languages:
                raise HTTPException(status_code=400, detail=f"Invalid language: {lang}")
        
        # Validate preprocessing mode
        if preprocessing_mode not in valid_preprocessing:
            raise HTTPException(status_code=400, detail=f"Invalid preprocessing mode: {preprocessing_mode}")
        
        # Validate confidence threshold
        if not 0 <= confidence_threshold <= 100:
            raise HTTPException(status_code=400, detail="Confidence threshold must be between 0 and 100")
        
        # Store configuration in Redis
        config_data = {
            "languages": languages,
            "confidence_threshold": confidence_threshold,
            "preprocessing_mode": preprocessing_mode,
            "updated_at": datetime.now().isoformat()
        }
        
        await redis_client.set("ocr_config", json.dumps(config_data))
        
        logger.info(f"OCR configuration updated: {config_data}")
        
        return {"message": "OCR configuration updated", "config": config_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR config update error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include other routes
app.include_router(router, prefix="/api")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )