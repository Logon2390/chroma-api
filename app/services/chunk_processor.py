import uuid
from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models.schemas import DocumentChunk, DocumentMetadata, FileType
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP

class ChunkProcessor:
    """Service for splitting document text into chunks.
    
    This class is responsible for processing text and splitting it into smaller chunks
    that can be stored in a vector database.
    """
    
    def split_text_into_chunks(
        self, 
        text: str, 
        metadata: Dict[str, Any], 
        chunk_size: int = CHUNK_SIZE, 
        chunk_overlap: int = CHUNK_OVERLAP
    ) -> List[DocumentChunk]:
        """Split text into chunks and create DocumentChunk objects for each.
        
        Args:
            text: The text content to split.
            metadata: Metadata associated with the document.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between consecutive chunks.
            
        Returns:
            A list of DocumentChunk objects.
        """
        # Create text splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Split text into chunks
        text_chunks = splitter.split_text(text)
        doc_id = str(uuid.uuid4())  # Generate a single document ID for all chunks
        
        # Create document chunks
        document_chunks = []
        
        # Ensure file_type is a proper FileType enum
        file_type = metadata.get("file_type")
        if isinstance(file_type, str):
            try:
                file_type = FileType(file_type.lower())
            except ValueError:
                file_type = FileType.TXT
        elif not isinstance(file_type, FileType):
            file_type = FileType.TXT
            
        # Format the document metadata
        document_metadata = DocumentMetadata(
            filename=metadata.get("filename", "unknown.txt"),
            file_type=file_type,
            content_length=metadata.get("content_length", len(text)),
            upload_timestamp=metadata.get("upload_timestamp", ""),
            additional_metadata={
                **metadata.get("additional_metadata", {}),
                "parent_doc_id": doc_id  # Add the parent document ID to metadata
            }
        )
        
        for i, chunk_text in enumerate(text_chunks):
            # Generate a unique ID for this chunk
            chunk_id = str(uuid.uuid4())
            
            # Create a DocumentChunk object
            chunk = DocumentChunk(
                id=chunk_id,
                text=chunk_text,
                metadata=document_metadata,
                embedding_id=chunk_id
            )
                      
            document_chunks.append(chunk)
            
        return document_chunks 