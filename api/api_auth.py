#!/usr/bin/env python3
"""
Authentication and authorization management
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional, Dict
from api_models import User, UserCreate

logger = logging.getLogger(__name__)

class AuthManager:
    """Handles authentication and authorization"""
    
    def __init__(self, database):
        self.db = database
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv('JWT_SECRET_KEY')
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 1440  # 24 hours
        
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable not set")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"JWT error: {e}")
            return None
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if username already exists
            existing_user = await self.db.get_user_by_username(user_data.username)
            if existing_user:
                raise ValueError("Username already exists")
            
            # Hash password
            hashed_password = self.hash_password(user_data.password)
            
            # Create user in database
            user_record = await self.db.create_user(user_data.username, hashed_password)
            
            # Return User object
            return User(
                id=user_record['id'],
                username=user_record['username'],
                created_at=user_record['created_at']
            )
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return access token"""
        try:
            # Get user from database
            user_record = await self.db.get_user_by_username(username)
            if not user_record:
                logger.warning(f"Authentication failed: user '{username}' not found")
                return None
            
            # Verify password
            if not self.verify_password(password, user_record['password_hash']):
                logger.warning(f"Authentication failed: invalid password for user '{username}'")
                return None
            
            # Create access token
            token_data = {
                "sub": str(user_record['id']),
                "username": user_record['username']
            }
            access_token = self.create_access_token(token_data)
            
            logger.info(f"User '{username}' authenticated successfully")
            return access_token
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        try:
            # Verify token
            payload = self.verify_token(token)
            if not payload:
                return None
            
            # Get user ID from token
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Get user from database
            user_record = await self.db.get_user_by_id(int(user_id))
            if not user_record:
                return None
            
            # Return User object
            return User(
                id=user_record['id'],
                username=user_record['username'],
                created_at=user_record['created_at']
            )
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an access token"""
        try:
            # Verify current token
            payload = self.verify_token(token)
            if not payload:
                return None
            
            # Create new token with same data
            new_token_data = {
                "sub": payload.get("sub"),
                "username": payload.get("username")
            }
            new_token = self.create_access_token(new_token_data)
            
            return new_token
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Get user from database
            user_record = await self.db.get_user_by_id(user_id)
            if not user_record:
                return False
            
            # Verify old password
            if not self.verify_password(old_password, user_record['password_hash']):
                return False
            
            # Hash new password
            new_password_hash = self.hash_password(new_password)
            
            # Update password in database
            query = "UPDATE users SET password_hash = $1 WHERE id = $2"
            await self.db.execute(query, new_password_hash, user_id)
            
            logger.info(f"Password changed for user ID {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False