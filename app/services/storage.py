"""
Supabase Storage Service

Handles file uploads to Supabase Storage bucket for receipt images.
Falls back to local storage if Supabase is not configured.
"""
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import UploadFile, HTTPException, status

from app.core.config import settings


# Local storage directory (fallback)
LOCAL_STORAGE_DIR = "/app/uploads"


class StorageService:
    """
    Service for handling file uploads.
    Uses Supabase Storage if configured, otherwise falls back to local storage.
    """
    
    def __init__(self):
        """Initialize storage service."""
        self._supabase_client = None
        self._use_local = not (settings.supabase_url and settings.supabase_key)
        
        # Create local storage directory if using local storage
        if self._use_local:
            os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
    
    @property
    def supabase_client(self):
        """Lazy initialization of Supabase client."""
        if self._supabase_client is None and not self._use_local:
            try:
                from supabase import create_client
                self._supabase_client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )
            except Exception as e:
                print(f"Warning: Could not initialize Supabase: {e}")
                self._use_local = True
                os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
        return self._supabase_client
    
    def _generate_unique_filename(
        self,
        user_id: int,
        original_filename: str
    ) -> str:
        """Generate a unique filename for storage."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = original_filename.replace(" ", "_")
        return f"{user_id}/{timestamp}_{unique_id}_{safe_filename}"
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: int
    ) -> str:
        """
        Upload a file and return the URL.
        Uses Supabase if configured, otherwise saves locally.
        """
        # Ensure local storage directory exists
        os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
        
        # Force check if we should use local (try to init supabase to trigger fallback)
        if not self._use_local:
            _ = self.supabase_client  # This will set _use_local if supabase fails
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/jpg"]
        content_type = file.content_type or "image/jpeg"
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {content_type}. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file contents
        try:
            file_bytes = await file.read()
            print(f"[DEBUG] Read {len(file_bytes)} bytes from file")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read file: {str(e)}"
            )
        
        # Generate unique filename
        filename = self._generate_unique_filename(
            user_id=user_id,
            original_filename=file.filename or "receipt.jpg"
        )
        
        print(f"[DEBUG] Using {'local' if self._use_local else 'Supabase'} storage")
        
        if self._use_local:
            return await self._upload_local(filename, file_bytes)
        else:
            return await self._upload_supabase(filename, file_bytes, content_type)
    
    async def _upload_local(self, filename: str, file_bytes: bytes) -> str:
        """Save file to local storage."""
        try:
            # Create user directory
            filepath = os.path.join(LOCAL_STORAGE_DIR, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write file
            with open(filepath, "wb") as f:
                f.write(file_bytes)
            
            # Return local URL (for Docker, this would be served statically)
            return f"file://{filepath}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file locally: {str(e)}"
            )
    
    async def _upload_supabase(self, filename: str, file_bytes: bytes, content_type: str) -> str:
        """Upload to Supabase Storage."""
        try:
            self.supabase_client.storage.from_(
                settings.supabase_bucket
            ).upload(
                path=filename,
                file=file_bytes,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"
                }
            )
            
            # Get public URL
            public_url = self.supabase_client.storage.from_(
                settings.supabase_bucket
            ).get_public_url(filename)
            
            return public_url
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to Supabase: {str(e)}"
            )


# Global instance
storage_service = StorageService()


async def upload_receipt_file(file: UploadFile, user_id: int) -> str:
    """Helper function to upload a receipt file."""
    return await storage_service.upload_file(file, user_id)
