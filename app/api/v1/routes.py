from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import List

from app.services.file_processor import FileProcessor
from app.services.vector_store import VectorStore
from app.models.schemas import UploadResponse, DocumentChunk, VectorStoreResponse


router = APIRouter(prefix="/api/v1", tags=["AI Vector API"])

# Factory functions for dependencies
def get_file_processor():
    return FileProcessor()

def get_vector_store():
    return VectorStore()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_processor: FileProcessor = Depends(get_file_processor)
):
    """Upload a file to be processed and stored in the vector database.
    
    The file will be processed to extract its text content, which will then
    be vectorized and stored in the vector database.
    
    Args:
        file: The file to upload (PDF, DOCX, or TXT).
        file_processor: The file processor service.
        
    Returns:
        Information about the processed file.
    """
    return await file_processor.process_upload(file)


@router.get("/documents/{doc_id}", response_model=DocumentChunk)
async def get_document(
    doc_id: str,
    vector_store: VectorStore = Depends(get_vector_store)
):
    """Retrieve a document from the vector store by its ID.
    
    Args:
        doc_id: The ID of the document to retrieve.
        vector_store: The vector store service.
        
    Returns:
        The document with the given ID.
        
    Raises:
        HTTPException: If the document is not found.
    """
    document = vector_store.get_document(doc_id)
    
    if not document:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
    
    return document


@router.delete("/documents/{doc_id}", response_model=VectorStoreResponse)
async def delete_document(
    doc_id: str,
    vector_store: VectorStore = Depends(get_vector_store)
):
    """Delete a document from the vector store.
    
    Args:
        doc_id: The ID of the document to delete.
        vector_store: The vector store service.
        
    Returns:
        The result of the delete operation.
    """
    return vector_store.delete_document(doc_id)


@router.get("/search", response_model=List[DocumentChunk])
async def search_documents(
    query: str = Query(..., description="The search query"),
    limit: int = Query(5, description="Maximum number of results to return"),
    vector_store: VectorStore = Depends(get_vector_store)
):
    """Search for documents similar to the query text.
    
    Args:
        query: The text to search for.
        limit: Maximum number of results to return.
        vector_store: The vector store service.
        
    Returns:
        A list of documents similar to the query.
    """
    return vector_store.search_similar(query, k=limit) 