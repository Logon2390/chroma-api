from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from app.models.schemas import FileType


class BaseExtractor(ABC):
    """Base class for all document extractors.
    
    This abstract class defines the interface that all document extractors
    must implement. It ensures a uniform API for extracting text content from
    different file types.
    """
    
    def __init__(self):
        """Initialize the extractor."""
        pass
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extract text content from a file.
        
        Args:
            file_path: Path to the file to extract text from.
            
        Returns:
            The extracted text content as a string.
            
        Raises:
            ValueError: If the file cannot be processed.
        """
        pass
    
    @abstractmethod
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            A dictionary containing metadata about the file.
            
        Raises:
            ValueError: If the file cannot be processed.
        """
        pass
    
    @classmethod
    @abstractmethod
    def supports_filetype(cls, file_type: FileType) -> bool:
        """Check if this extractor supports the given file type.
        
        Args:
            file_type: The type of file to check support for.
            
        Returns:
            True if this extractor supports the given file type, False otherwise.
        """
        pass 