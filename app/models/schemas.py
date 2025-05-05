from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class UploadResponse(BaseModel):
    """Response model for file upload endpoint"""
    filename: str
    file_type: FileType
    content_length: int
    vector_id: str
    success: bool
    message: str


class DocumentMetadata(BaseModel):
    """Metadata associated with a document"""
    filename: str
    file_type: FileType
    content_length: int
    upload_timestamp: str
    additional_metadata: Optional[Dict[str, Any]] = None


class DocumentChunk(BaseModel):
    """A chunk of text from a document with its metadata"""
    id: str
    text: str
    metadata: DocumentMetadata
    embedding_id: Optional[str] = None


class VectorStoreResponse(BaseModel):
    """Response from the vector store operations"""
    success: bool
    message: str
    document_ids: Optional[List[str]] = None
    error: Optional[str] = None 