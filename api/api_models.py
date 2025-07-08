#!/usr/bin/env python3
"""
Data models and Pydantic schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# User models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Folder models
class FolderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class FolderCreate(FolderBase):
    pass

class Folder(FolderBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response models
class ResponseBase(BaseModel):
    ocr_text: Optional[str] = None
    ai_response: Optional[str] = None

class ResponseCreate(ResponseBase):
    user_id: int
    folder_id: Optional[int] = None

class Response(ResponseBase):
    id: int
    user_id: int
    folder_id: Optional[int] = None
    created_at: datetime
    folder: Optional[Folder] = None
    
    class Config:
        from_attributes = True

# API response models
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int

# OCR Job models
class OCRJob(BaseModel):
    file_path: str
    timestamp: Optional[int] = None
    type: str = "screenshot"
    user_id: Optional[int] = None
    folder_id: Optional[int] = None

class OCRResult(BaseModel):
    text: str
    confidence: float
    language: str
    processing_time: float

# AI Analysis models
class AIAnalysisRequest(BaseModel):
    ocr_text: str
    context: Optional[str] = None
    language: str = "auto"

class AIAnalysisResult(BaseModel):
    analysis: str
    model_used: str
    processing_time: float
    tokens_used: Optional[int] = None

# File upload models
class FileUpload(BaseModel):
    filename: str
    content_type: str
    size: int
    
class UploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    message: str