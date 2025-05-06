import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import CHROMA_DB_DIR, EMBEDDING_MODEL
from app.models.schemas import DocumentMetadata, DocumentChunk, VectorStoreResponse


class VectorStore:
    """Encapsulates vector storage and retrieval functionality using ChromaDB and LangChain.
    
    This class is responsible for managing the connection to the ChromaDB vector database
    and providing methods to store, retrieve, and search documents.
    """
    
    def __init__(self, collection_name: str = "documents"):
        """Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection to use.
        """
        self.collection_name = collection_name
        self.db_path = Path(CHROMA_DB_DIR)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Initialize the vector store
        self.db = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.db_path)
        )
    
    def add_document(self, text: str, metadata: Dict[str, Any]) -> VectorStoreResponse:
        """Add a document to the vector store.
        
        Args:
            text: The text content of the document to add.
            metadata: Metadata associated with the document.
            
        Returns:
            A VectorStoreResponse containing the result of the operation.
        """
        try:
            # Generate a unique ID for the document
            doc_id = str(uuid.uuid4())
            
            # Add document to vector store
            self.db.add_texts(
                texts=[text],
                metadatas=[{**metadata, "doc_id": doc_id}],
                ids=[doc_id]
            )
            
            return VectorStoreResponse(
                success=True,
                message="Document added successfully",
                document_ids=[doc_id]
            )
        except Exception as e:
            return VectorStoreResponse(
                success=False,
                message="Failed to add document to vector store",
                error=str(e)
            )
    
    def search_similar(self, query_text: str, k: int = 5) -> List[DocumentChunk]:
        """Search for documents similar to the query text.
        
        Args:
            query_text: The text to search for.
            k: Number of similar documents to return.
            
        Returns:
            A list of DocumentChunk objects representing the most similar documents.
        """
        results = self.db.similarity_search_with_relevance_scores(query_text, k=k)
        
        # Convert results to DocumentChunk objects
        documents = []
        for doc, score in results:
            # Extract metadata from the document
            metadata = doc.metadata
            doc_id = metadata.get("doc_id", str(uuid.uuid4()))
            
            # Create document chunk
            chunk = DocumentChunk(
                id=doc_id,
                text=doc.page_content,
                metadata=metadata,
                embedding_id=doc_id
            )
            
            documents.append(chunk)
        
        return documents
    
    def delete_document(self, doc_id: str) -> VectorStoreResponse:
        """Delete a document from the vector store.
        
        Args:
            doc_id: The ID of the document to delete.
            
        Returns:
            A VectorStoreResponse containing the result of the operation.
        """
        try:
            self.db.delete([doc_id])
            return VectorStoreResponse(
                success=True,
                message=f"Document {doc_id} deleted successfully"
            )
        except Exception as e:
            return VectorStoreResponse(
                success=False,
                message=f"Failed to delete document {doc_id}",
                error=str(e)
            )
    
    def get_document(self, doc_id: str) -> Optional[DocumentChunk]:
        """Retrieve a document from the vector store by ID.
        
        Args:
            doc_id: The ID of the document to retrieve.
            
        Returns:
            A DocumentChunk if found, None otherwise.
        """
        # This is a simplified implementation as ChromaDB doesn't have a direct
        # get_document method. In a production environment, you might use additional
        # filtering or a separate document store for direct lookups.
        results = self.db.similarity_search(
            query="",  # Empty query to bypass similarity search
            k=100,     # Retrieve a large number to increase chances of finding the document
            filter={"doc_id": doc_id}  # Filter by document ID
        )
        
        for doc in results:
            metadata = doc.metadata
            if metadata.get("doc_id") == doc_id:
                return DocumentChunk(
                    id=doc_id,
                    text=doc.page_content,
                    metadata=metadata,
                    embedding_id=doc_id
                )
        
        return None 