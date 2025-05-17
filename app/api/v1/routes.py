from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import List

from app.services.file_processor import FileProcessor
from app.models.schemas import UploadResponse, DocumentChunk, VectorStoreResponse


router = APIRouter(prefix="/api/v1", tags=["AI Vector API"])

# Factory functions for dependencies
def get_file_processor():
    return FileProcessor()



@router.post("/upload", response_model=List[UploadResponse])
async def upload_file(
    files: List[UploadFile] = File(...),
    file_processor: FileProcessor = Depends(get_file_processor)
):
    """Upload multiple files to be processed and stored in the vector database.
    
    The files will be processed to extract their text content, which will then
    be vectorized and stored in the vector database.
    
    Args:
        files: List of files to upload (PDF, DOCX, or TXT).
        file_processor: The file processor service.
        
    Returns:
        List of information about each processed file.
    """
    responses = []
    for file in files:
        response = await file_processor.process_upload(file)
        responses.append(response)
    return responses