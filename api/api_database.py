#!/usr/bin/env python3
"""
Database connection and operations
"""

import os
import asyncpg
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Database connection and operations manager"""
    
    def __init__(self):
        self.pool = None
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query and return result"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetchval(self, query: str, *args):
        """Fetch single value"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def create_tables(self):
        """Create database tables"""
        try:
            async with self.pool.acquire() as conn:
                # Users table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Folders table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS folders (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(user_id, name)
                    )
                """)
                
                # Responses table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS responses (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
                        ocr_text TEXT,
                        ai_response TEXT,
                        image_path VARCHAR(500),
                        ocr_confidence FLOAT DEFAULT 0,
                        ocr_language VARCHAR(50),
                        ai_model VARCHAR(50),
                        ai_tokens INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_responses_folder_id ON responses(folder_id)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_responses_created_at ON responses(created_at)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id)")
                
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    # User operations
    async def create_user(self, username: str, password_hash: str) -> Dict:
        """Create a new user"""
        query = """
            INSERT INTO users (username, password_hash)
            VALUES ($1, $2)
            RETURNING id, username, created_at
        """
        return await self.fetchrow(query, username, password_hash)
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = $1"
        return await self.fetchrow(query, username)
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = $1"
        return await self.fetchrow(query, user_id)
    
    # Folder operations
    async def create_folder(self, user_id: int, name: str) -> Dict:
        """Create a new folder"""
        query = """
            INSERT INTO folders (user_id, name)
            VALUES ($1, $2)
            RETURNING id, user_id, name, created_at
        """
        return await self.fetchrow(query, user_id, name)
    
    async def get_folders_by_user(self, user_id: int) -> List[Dict]:
        """Get all folders for a user"""
        query = """
            SELECT * FROM folders 
            WHERE user_id = $1 
            ORDER BY name ASC
        """
        return await self.fetch(query, user_id)
    
    async def get_folder_by_id(self, folder_id: int, user_id: int) -> Optional[Dict]:
        """Get folder by ID (with user verification)"""
        query = """
            SELECT * FROM folders 
            WHERE id = $1 AND user_id = $2
        """
        return await self.fetchrow(query, folder_id, user_id)
    
    async def delete_folder(self, folder_id: int, user_id: int) -> bool:
        """Delete a folder"""
        query = """
            DELETE FROM folders 
            WHERE id = $1 AND user_id = $2
        """
        result = await self.execute(query, folder_id, user_id)
        return result == "DELETE 1"
    
    # Response operations
    async def create_response(self, user_id: int, folder_id: Optional[int], 
                            ocr_text: str, ai_response: str, image_path: str) -> Dict:
        """Create a new response"""
        query = """
            INSERT INTO responses (user_id, folder_id, ocr_text, ai_response, image_path)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, user_id, folder_id, ocr_text, ai_response, image_path, created_at
        """
        return await self.fetchrow(query, user_id, folder_id, ocr_text, ai_response, image_path)
    
    async def get_responses_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get responses for a user with pagination"""
        query = """
            SELECT r.*, f.name as folder_name
            FROM responses r
            LEFT JOIN folders f ON r.folder_id = f.id
            WHERE r.user_id = $1
            ORDER BY r.created_at DESC
            LIMIT $2 OFFSET $3
        """
        return await self.fetch(query, user_id, limit, offset)
    
    async def get_responses_by_folder(self, folder_id: int, user_id: int, 
                                    limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get responses in a specific folder"""
        query = """
            SELECT r.*, f.name as folder_name
            FROM responses r
            LEFT JOIN folders f ON r.folder_id = f.id
            WHERE r.folder_id = $1 AND r.user_id = $2
            ORDER BY r.created_at DESC
            LIMIT $3 OFFSET $4
        """
        return await self.fetch(query, folder_id, user_id, limit, offset)
    
    async def get_response_by_id(self, response_id: int, user_id: int) -> Optional[Dict]:
        """Get response by ID (with user verification)"""
        query = """
            SELECT r.*, f.name as folder_name
            FROM responses r
            LEFT JOIN folders f ON r.folder_id = f.id
            WHERE r.id = $1 AND r.user_id = $2
        """
        return await self.fetchrow(query, response_id, user_id)
    
    async def delete_response(self, response_id: int, user_id: int) -> bool:
        """Delete a response"""
        query = """
            DELETE FROM responses 
            WHERE id = $1 AND user_id = $2
        """
        result = await self.execute(query, response_id, user_id)
        return result == "DELETE 1"
    
    async def count_responses_by_user(self, user_id: int) -> int:
        """Count total responses for a user"""
        query = "SELECT COUNT(*) FROM responses WHERE user_id = $1"
        return await self.fetchval(query, user_id)
    
    async def count_responses_by_folder(self, folder_id: int, user_id: int) -> int:
        """Count responses in a folder"""
        query = """
            SELECT COUNT(*) FROM responses 
            WHERE folder_id = $1 AND user_id = $2
        """
        return await self.fetchval(query, folder_id, user_id)
    
    async def move_response_to_folder(self, response_id: int, folder_id: Optional[int], user_id: int) -> bool:
        """Move response to a different folder"""
        query = """
            UPDATE responses 
            SET folder_id = $1 
            WHERE id = $2 AND user_id = $3
        """
        result = await self.execute(query, folder_id, response_id, user_id)
        return result == "UPDATE 1"