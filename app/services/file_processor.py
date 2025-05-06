import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import UploadFile, HTTPException

from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE
from app.models.schemas import FileType, UploadResponse
from app.services.extractors.base import BaseExtractor
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.docx_extractor import DocxExtractor
from app.services.extractors.txt_extractor import TxtExtractor
from app.services.vector_store import VectorStore


class FileProcessor:
    """Handles file processing, extraction, and storage.
    
    This class coordinates the file processing workflow, from validating uploaded files
    to extracting their content and storing them in the vector database.
    """
    
    def __init__(self):
        """Initialize the file processor."""
        self.upload_dir = Path(UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize extractors
        self.extractors: List[BaseExtractor] = [
            PDFExtractor(),
            DocxExtractor(),
            TxtExtractor()
        ]
        
        # Initialize vector store
        self.vector_store = VectorStore()
    
    def _get_file_type(self, filename: str) -> Optional[FileType]:
        """Determine the file type from the filename.
        
        Args:
            filename: The name of the file.
            
        Returns:
            The file type enum, or None if the file type is not supported.
        """
        extension = filename.split('.')[-1].lower()
        
        if extension == 'pdf':
            return FileType.PDF
        elif extension == 'docx':
            return FileType.DOCX
        elif extension == 'txt':
            return FileType.TXT
        else:
            return None
    
    def _get_extractor_for_file_type(self, file_type: FileType) -> Optional[BaseExtractor]:
        """Get the appropriate extractor for the given file type.
        
        Args:
            file_type: The type of file to get an extractor for.
            
        Returns:
            An extractor instance, or None if no extractor supports the file type.
        """
        for extractor in self.extractors:
            if extractor.supports_filetype(file_type):
                return extractor
        
        return None
    
    async def process_upload(self, upload_file: UploadFile) -> UploadResponse:
        """Process an uploaded file.
        
        Args:
            upload_file: The uploaded file.
            
        Returns:
            A response containing the result of processing the upload.
            
        Raises:
            HTTPException: If the file type is not supported or the file is too large.
        """
        # Validate file size
        if upload_file.size and upload_file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE} bytes."
            )
        
        # Check file type
        file_type = self._get_file_type(upload_file.filename)
        if not file_type:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {upload_file.filename}"
            )
        
        # Get appropriate extractor
        extractor = self._get_extractor_for_file_type(file_type)
        if not extractor:
            raise HTTPException(
                status_code=415,
                detail=f"No extractor available for file type: {file_type}"
            )
        
        # Save file to disk
        file_path = self.upload_dir / upload_file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        try:
            # Extract text and metadata
            text_content = extractor.extract_text(file_path)
            metadata = extractor.get_metadata(file_path)
            
            # Add a timestamp
            metadata["upload_timestamp"] = datetime.now().isoformat()
            
            # Store in vector database
            vector_response = self.vector_store.add_document(text_content, metadata)
            
            if not vector_response.success:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to store document in vector database: {vector_response.error}"
                )
            
            # Create response
            vector_id = vector_response.document_ids[0] if vector_response.document_ids else ""
            
            return UploadResponse(
                filename=upload_file.filename,
                file_type=file_type,
                content_length=len(text_content),
                vector_id=vector_id,
                success=True,
                message="File processed and stored successfully"
            )
        
        except Exception as e:
            # Handle errors
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )
        finally:
            # Close the file
            upload_file.file.close()
            
            # Optionally delete the file after processing
            # Uncomment the following line if you want to delete files after processing
            # file_path.unlink(missing_ok=True) 