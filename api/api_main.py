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
@app.get("/api/health")
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
@app.get("/api/info")
async def get_info():
    """Get server information"""
    return {
        "name": "Screenshot AI Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

# Authentication endpoints
@app.post("/api/auth/login")
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

@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    """User registration - now open to public"""
    try:
        user = await auth_manager.create_user(user_data)
        return {"message": "User created successfully", "user_id": user.id}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/refresh")
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

@app.get("/api/users/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat()
    }

# Screenshot upload endpoint
@app.post("/api/screenshot")
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