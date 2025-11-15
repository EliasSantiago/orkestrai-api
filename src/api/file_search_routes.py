"""
File Search API routes for RAG (Retrieval-Augmented Generation).

This module provides endpoints for managing File Search Stores and Files,
allowing users to upload documents for RAG with their agents.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from src.database import get_db
from src.models import FileSearchStore, FileSearchFile, User
from src.services.file_search.store_manager import FileSearchStoreManager
from src.services.file_search.file_manager import FileSearchFileManager
from src.api.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/file-search", tags=["file-search"])


# Request/Response Models
class FileSearchStoreCreate(BaseModel):
    """Request model for creating a File Search Store."""
    display_name: str = Field(..., description="User-friendly name for the store", min_length=1, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "display_name": "Documentos da Empresa"
            }
        }


class FileSearchStoreResponse(BaseModel):
    """Response model for File Search Store."""
    id: int
    display_name: str
    google_store_name: str
    is_active: bool
    created_at: str
    file_count: int = 0
    
    class Config:
        from_attributes = True


class FileSearchFileResponse(BaseModel):
    """Response model for File Search File."""
    id: int
    store_id: int
    display_name: Optional[str]
    google_file_name: Optional[str] = None  # Can be None if extraction from Google API fails
    file_type: Optional[str]
    size_bytes: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


# Store Endpoints
@router.post("/stores", response_model=FileSearchStoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    request: FileSearchStoreCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new File Search Store.
    
    Each user can create multiple stores to organize their documents.
    Stores are isolated per user - users can only see their own stores.
    """
    try:
        manager = FileSearchStoreManager()
        store_info = manager.create_store(request.display_name)
        
        # Save to database
        store = FileSearchStore(
            user_id=user_id,
            display_name=request.display_name,
            google_store_name=store_info['name'],
            is_active=True
        )
        db.add(store)
        db.commit()
        db.refresh(store)
        
        logger.info(f"Created file search store {store.id} for user {user_id}")
        
        return FileSearchStoreResponse(
            id=store.id,
            display_name=store.display_name,
            google_store_name=store.google_store_name,
            is_active=store.is_active,
            created_at=store.created_at.isoformat(),
            file_count=0
        )
    except Exception as e:
        logger.error(f"Error creating file search store: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create file search store: {str(e)}"
        )


@router.get("/stores", response_model=List[FileSearchStoreResponse])
async def list_stores(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all File Search Stores for the current user.
    
    Users can only see their own stores - isolation is enforced.
    """
    try:
        stores = db.query(FileSearchStore).filter(
            FileSearchStore.user_id == user_id
        ).all()
        
        result = []
        for store in stores:
            file_count = db.query(FileSearchFile).filter(
                FileSearchFile.store_id == store.id
            ).count()
            
            result.append(FileSearchStoreResponse(
                id=store.id,
                display_name=store.display_name,
                google_store_name=store.google_store_name,
                is_active=store.is_active,
                created_at=store.created_at.isoformat(),
                file_count=file_count
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error listing file search stores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list file search stores: {str(e)}"
        )


@router.get("/stores/{store_id}", response_model=FileSearchStoreResponse)
async def get_store(
    store_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific File Search Store.
    
    Users can only access their own stores - isolation is enforced.
    Security: This endpoint verifies that the store belongs to the authenticated user.
    """
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id  # CRITICAL: Always filter by user_id
    ).first()
    
    if not store:
        # Return 404 to avoid information leakage about other users' stores
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File Search Store not found"
        )
    
    file_count = db.query(FileSearchFile).filter(
        FileSearchFile.store_id == store.id
    ).count()
    
    return FileSearchStoreResponse(
        id=store.id,
        display_name=store.display_name,
        google_store_name=store.google_store_name,
        is_active=store.is_active,
        created_at=store.created_at.isoformat(),
        file_count=file_count
    )


@router.delete("/stores/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    store_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a File Search Store.
    
    This will also delete all files in the store.
    Users can only delete their own stores - isolation is enforced.
    Security: This endpoint verifies that the store belongs to the authenticated user.
    """
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id  # CRITICAL: Always filter by user_id
    ).first()
    
    if not store:
        # Return 404 to avoid information leakage about other users' stores
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File Search Store not found"
        )
    
    try:
        # Delete from Google
        manager = FileSearchStoreManager()
        manager.delete_store(store.google_store_name)
        
        # Delete from database (cascade will delete files)
        db.delete(store)
        db.commit()
        
        logger.info(f"Deleted file search store {store_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Error deleting file search store: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file search store: {str(e)}"
        )


# File Endpoints
@router.post("/stores/{store_id}/files", response_model=FileSearchFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    store_id: int,
    file: UploadFile = File(..., description="File to upload (max 100 MB)"),
    display_name: Optional[str] = Form(None, description="Optional display name for the file"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Upload a file to a File Search Store.
    
    The file will be automatically indexed and made available for RAG.
    Maximum file size: 100 MB (as per Google documentation).
    Users can only upload to their own stores - isolation is enforced.
    Security: This endpoint verifies that the store belongs to the authenticated user.
    """
    # CRITICAL: Verify store belongs to user - always filter by user_id
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id  # CRITICAL: Always filter by user_id
    ).first()
    
    if not store:
        # Return 404 to avoid information leakage about other users' stores
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File Search Store not found"
        )
    
    if not store.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File Search Store is not active"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size (100 MB limit)
        file_manager = FileSearchFileManager()
        file_manager.validate_file_size(file_size)
        
        # Create file-like object from bytes
        import io
        file_obj = io.BytesIO(file_content)
        
        # Detect MIME type
        # FastAPI's UploadFile.content_type may be None or incorrect
        # We'll let file_manager detect it from filename if needed
        mime_type = file.content_type if file.content_type else None
        
        # Log for debugging
        logger.debug(f"File upload: filename='{file.filename}', content_type='{file.content_type}', provided_mime_type='{mime_type}'")
        
        # Upload and import
        # file_manager will detect MIME type from filename if not provided
        file_info = await file_manager.upload_and_import(
            file_content=file_obj,
            file_name=file.filename or "unnamed",
            store_name=store.google_store_name,
            display_name=display_name or file.filename,
            mime_type=mime_type  # Pass MIME type explicitly (may be None, will be detected)
        )
        
        # Save to database
        # Use None instead of empty string for google_file_name if not available
        google_file_name = file_info.get('name', '').strip()
        if not google_file_name:
            google_file_name = None  # Use None instead of empty string to avoid unique constraint violation
        
        db_file = FileSearchFile(
            store_id=store_id,
            display_name=display_name or file.filename,
            google_file_name=google_file_name,
            file_type=file.content_type,
            size_bytes=file_info.get('size_bytes', file_size),
            status='completed'  # Assuming success if no exception
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        logger.info(f"Uploaded file {db_file.id} to store {store_id} for user {user_id}")
        
        return FileSearchFileResponse(
            id=db_file.id,
            store_id=db_file.store_id,
            display_name=db_file.display_name,
            google_file_name=db_file.google_file_name,
            file_type=db_file.file_type,
            size_bytes=db_file.size_bytes,
            status=db_file.status,
            error_message=db_file.error_message,
            created_at=db_file.created_at.isoformat()
        )
        
    except ValueError as e:
        # File size validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/stores/{store_id}/files", response_model=List[FileSearchFileResponse])
async def list_files(
    store_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all files in a File Search Store.
    
    Users can only see files in their own stores - isolation is enforced.
    Security: This endpoint verifies that the store belongs to the authenticated user.
    """
    # CRITICAL: Verify store belongs to user - always filter by user_id
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id  # CRITICAL: Always filter by user_id
    ).first()
    
    if not store:
        # Return 404 to avoid information leakage about other users' stores
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File Search Store not found"
        )
    
    files = db.query(FileSearchFile).filter(
        FileSearchFile.store_id == store_id
    ).all()
    
    return [
        FileSearchFileResponse(
            id=file.id,
            store_id=file.store_id,
            display_name=file.display_name,
            google_file_name=file.google_file_name,
            file_type=file.file_type,
            size_bytes=file.size_bytes,
            status=file.status,
            error_message=file.error_message,
            created_at=file.created_at.isoformat()
        )
        for file in files
    ]


@router.get("/stores/{store_id}/files/{file_id}", response_model=FileSearchFileResponse)
async def get_file(
    store_id: int,
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific file from a File Search Store.
    
    Users can only access files in their own stores - isolation is enforced.
    Security: This endpoint verifies that both the store and file belong to the authenticated user.
    """
    # CRITICAL: Verify store belongs to user - always filter by user_id
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id  # CRITICAL: Always filter by user_id
    ).first()
    
    if not store:
        # Return 404 to avoid information leakage about other users' stores
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File Search Store not found"
        )
    
    # CRITICAL: Verify file belongs to the store (which already belongs to user)
    file = db.query(FileSearchFile).filter(
        FileSearchFile.id == file_id,
        FileSearchFile.store_id == store_id  # Ensures file belongs to user's store
    ).first()
    
    if not file:
        # Return 404 to avoid information leakage about other users' files
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileSearchFileResponse(
        id=file.id,
        store_id=file.store_id,
        display_name=file.display_name,
        google_file_name=file.google_file_name,
        file_type=file.file_type,
        size_bytes=file.size_bytes,
        status=file.status,
        error_message=file.error_message,
        created_at=file.created_at.isoformat()
    )


@router.delete("/stores/{store_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    store_id: int,
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a file from a File Search Store.
    
    Users can only delete files from their own stores - isolation is enforced.
    Security: This endpoint verifies that both the store and file belong to the authenticated user.
    """
    # CRITICAL: Verify store belongs to user - always filter by user_id
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id  # CRITICAL: Always filter by user_id
    ).first()
    
    if not store:
        # Return 404 to avoid information leakage about other users' stores
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File Search Store not found"
        )
    
    # CRITICAL: Verify file belongs to the store (which already belongs to user)
    file = db.query(FileSearchFile).filter(
        FileSearchFile.id == file_id,
        FileSearchFile.store_id == store_id  # Ensures file belongs to user's store
    ).first()
    
    if not file:
        # Return 404 to avoid information leakage about other users' files
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete from Google
        file_manager = FileSearchFileManager()
        file_manager.delete_file(file.google_file_name)
        
        # Delete from database
        db.delete(file)
        db.commit()
        
        logger.info(f"Deleted file {file_id} from store {store_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

