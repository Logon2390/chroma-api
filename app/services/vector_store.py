import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import CHROMA_DB_DIR, EMBEDDING_MODEL
from app.models.schemas import DocumentMetadata, DocumentChunk, VectorStoreResponse, FileType


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
            
            # Validate and format metadata to match DocumentMetadata schema
            if not isinstance(metadata.get("file_type"), FileType) and isinstance(metadata.get("file_type"), str):
                # Convert string to FileType enum if needed
                metadata["file_type"] = FileType(metadata["file_type"].lower())
                
            # Ensure content_length is present
            if "content_length" not in metadata:
                metadata["content_length"] = len(text)
                
            # Ensure required fields are present
            required_fields = ["filename", "file_type", "content_length", "upload_timestamp"]
            for field in required_fields:
                if field not in metadata:
                    raise ValueError(f"Required metadata field '{field}' is missing")
            
            # Prepare a flattened version of metadata for Chroma
            # Chroma only accepts simple types (str, int, float, bool)
            chroma_metadata = {}
            
            # Add standard fields
            chroma_metadata["doc_id"] = doc_id
            chroma_metadata["filename"] = metadata["filename"]
            chroma_metadata["content_length"] = metadata["content_length"]
            chroma_metadata["upload_timestamp"] = metadata["upload_timestamp"]
            
            # Handle file_type - convert enum to string
            if isinstance(metadata["file_type"], FileType):
                chroma_metadata["file_type"] = metadata["file_type"].value
            else:
                chroma_metadata["file_type"] = str(metadata["file_type"])
            
            # Add any additional simple metadata fields
            # We'll skip nested dictionaries and complex objects
            if "additional_metadata" in metadata and isinstance(metadata["additional_metadata"], dict):
                for key, value in metadata["additional_metadata"].items():
                    # Only include simple types
                    if isinstance(value, (str, int, float, bool)):
                        chroma_metadata[key] = value
            
            # Add document to vector store with simplified metadata
            self.db.add_texts(
                texts=[text],
                metadatas=[chroma_metadata],
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
            
            # Ensure file_type is a proper FileType enum
            file_type = metadata.get("file_type")
            if isinstance(file_type, str):
                try:
                    file_type = FileType(file_type.lower())
                except ValueError:
                    # Default to TXT if invalid
                    file_type = FileType.TXT
            elif not isinstance(file_type, FileType):
                file_type = FileType.TXT
            
            # Format metadata to match DocumentMetadata schema
            document_metadata = DocumentMetadata(
                filename=metadata.get("filename", "unknown.txt"),
                file_type=file_type,
                content_length=metadata.get("content_length", len(doc.page_content)),
                upload_timestamp=metadata.get("upload_timestamp", ""),
                additional_metadata=metadata
            )
            
            # Create document chunk
            chunk = DocumentChunk(
                id=doc_id,
                text=doc.page_content,
                metadata=document_metadata,
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
                # Ensure file_type is a proper FileType enum
                file_type = metadata.get("file_type")
                if isinstance(file_type, str):
                    try:
                        file_type = FileType(file_type.lower())
                    except ValueError:
                        # Default to TXT if invalid
                        file_type = FileType.TXT
                elif not isinstance(file_type, FileType):
                    file_type = FileType.TXT
                
                # Format metadata to match DocumentMetadata schema
                document_metadata = DocumentMetadata(
                    filename=metadata.get("filename", "unknown.txt"),
                    file_type=file_type,
                    content_length=metadata.get("content_length", len(doc.page_content)),
                    upload_timestamp=metadata.get("upload_timestamp", ""),
                    additional_metadata=metadata
                )
                
                return DocumentChunk(
                    id=doc_id,
                    text=doc.page_content,
                    metadata=document_metadata,
                    embedding_id=doc_id
                )
        
        return None 