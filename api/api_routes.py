#!/usr/bin/env python3
"""
API Routes for the screenshot analysis system
"""

import os
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as redis
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import tempfile

from api_models import User, FolderCreate, Folder, Response, PaginatedResponse
from api_auth import AuthManager
from api_database import Database

logger = logging.getLogger(__name__)

router = APIRouter()

# Security
security = HTTPBearer()

# Dependency functions that access global variables from api_main
def get_database():
    """Get database instance"""
    try:
        import api_main
        return api_main.db
    except (ImportError, AttributeError) as e:
        logger.error(f"Database dependency not available: {e}")
        raise HTTPException(status_code=500, detail="Database service unavailable")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        import api_main
        token = credentials.credentials
        user = await api_main.auth_manager.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def get_redis():
    """Get Redis client"""
    try:
        import api_main
        return api_main.redis_client
    except (ImportError, AttributeError) as e:
        logger.error(f"Redis dependency not available: {e}")
        raise HTTPException(status_code=500, detail="Redis service unavailable")

@router.get("/folders", response_model=List[Folder])
async def get_folders(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get all folders for the current user"""
    try:
        folders = await db.get_folders_by_user(current_user.id)
        return [
            Folder(
                id=folder['id'],
                name=folder['name'],
                user_id=folder['user_id'],
                created_at=folder['created_at']
            )
            for folder in folders
        ]
    except Exception as e:
        logger.error(f"Error getting folders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/folders", response_model=Folder)
async def create_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Create a new folder"""
    try:
        folder = await db.create_folder(current_user.id, folder_data.name)
        return Folder(
            id=folder['id'],
            name=folder['name'],
            user_id=folder['user_id'],
            created_at=folder['created_at']
        )
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Folder name already exists")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Delete a folder"""
    try:
        success = await db.delete_folder(folder_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        return {"message": "Folder deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting folder: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/responses", response_model=PaginatedResponse)
async def get_responses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    folder_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get responses with pagination"""
    try:
        offset = (page - 1) * per_page
        
        if folder_id:
            # Get responses from specific folder
            responses = await db.get_responses_by_folder(folder_id, current_user.id, per_page, offset)
            total = await db.count_responses_by_folder(folder_id, current_user.id)
        else:
            # Get all responses for user
            responses = await db.get_responses_by_user(current_user.id, per_page, offset)
            total = await db.count_responses_by_user(current_user.id)
        
        pages = (total + per_page - 1) // per_page
        
        return PaginatedResponse(
            items=[
                {
                    "id": response['id'],
                    "ocr_text": response['ocr_text'],
                    "ai_response": response['ai_response'],
                    "folder_id": response['folder_id'],
                    "folder_name": response.get('folder_name'),
                    "created_at": response['created_at'].isoformat()
                }
                for response in responses
            ],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    except Exception as e:
        logger.error(f"Error getting responses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/responses/{response_id}")
async def get_response(
    response_id: int,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get a specific response"""
    try:
        response = await db.get_response_by_id(response_id, current_user.id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        return {
            "id": response['id'],
            "ocr_text": response['ocr_text'],
            "ai_response": response['ai_response'],
            "folder_id": response['folder_id'],
            "folder_name": response.get('folder_name'),
            "created_at": response['created_at'].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/responses/{response_id}")
async def delete_response(
    response_id: int,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Delete a response"""
    try:
        success = await db.delete_response(response_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Response not found")
        
        return {"message": "Response deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/responses/{response_id}/folder")
async def move_response_to_folder(
    response_id: int,
    folder_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Move response to a different folder"""
    try:
        # Verify folder exists if folder_id is provided
        if folder_id:
            folder = await db.get_folder_by_id(folder_id, current_user.id)
            if not folder:
                raise HTTPException(status_code=404, detail="Folder not found")
        
        success = await db.move_response_to_folder(response_id, folder_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Response not found")
        
        return {"message": "Response moved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload")
async def manual_upload(
    image: UploadFile = File(...),
    folder_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database),
    redis_client = Depends(get_redis)
):
    """Manual upload for mobile/web interface"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Verify folder if provided
        if folder_id:
            folder = await db.get_folder_by_id(folder_id, current_user.id)
            if not folder:
                raise HTTPException(status_code=404, detail="Folder not found")
        
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
            "user_id": current_user.id,
            "folder_id": folder_id,
            "type": "manual_upload"
        }
        
        # Add to Redis queue
        await redis_client.lpush("ocr_queue", str(job_data))
        
        logger.info(f"Manual upload queued for processing: {file_path}")
        
        return {"message": "Image uploaded and queued for processing", "status": "queued"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/export/{response_id}/pdf")
async def export_response_pdf(
    response_id: int,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Export response as PDF"""
    try:
        response = await db.get_response_by_id(response_id, current_user.id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        # Create PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"AI Analysis Report")
        
        # Date
        p.setFont("Helvetica", 12)
        created_at = response['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        p.drawString(50, height - 80, f"Created: {created_at}")
        
        # Folder info
        if response.get('folder_name'):
            p.drawString(50, height - 100, f"Folder: {response['folder_name']}")
        
        # OCR Text
        y_position = height - 140
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "Extracted Text:")
        
        y_position -= 20
        p.setFont("Helvetica", 10)
        
        # Split OCR text into lines
        ocr_text = response.get('ocr_text', 'No text extracted')
        lines = ocr_text.split('\n')
        for line in lines:
            if y_position < 50:
                p.showPage()
                y_position = height - 50
            
            # Wrap long lines
            while len(line) > 80:
                p.drawString(50, y_position, line[:80])
                line = line[80:]
                y_position -= 15
                if y_position < 50:
                    p.showPage()
                    y_position = height - 50
            
            p.drawString(50, y_position, line)
            y_position -= 15
        
        # AI Response
        y_position -= 20
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "AI Analysis:")
        
        y_position -= 20
        p.setFont("Helvetica", 10)
        
        # Split AI response into lines
        ai_response = response.get('ai_response', 'No analysis available')
        lines = ai_response.split('\n')
        for line in lines:
            if y_position < 50:
                p.showPage()
                y_position = height - 50
            
            # Wrap long lines
            while len(line) > 80:
                p.drawString(50, y_position, line[:80])
                line = line[80:]
                y_position -= 15
                if y_position < 50:
                    p.showPage()
                    y_position = height - 50
            
            p.drawString(50, y_position, line)
            y_position -= 15
        
        p.save()
        buffer.seek(0)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type='application/pdf',
            filename=f'analysis_report_{response_id}.pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get user statistics"""
    try:
        total_responses = await db.count_responses_by_user(current_user.id)
        folders = await db.get_folders_by_user(current_user.id)
        
        return {
            "total_responses": total_responses,
            "total_folders": len(folders),
            "user_since": current_user.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")