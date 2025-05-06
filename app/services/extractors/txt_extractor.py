import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from app.services.extractors.base import BaseExtractor
from app.models.schemas import FileType


class TxtExtractor(BaseExtractor):
    """Extractor for TXT files.
    
    This class provides functionality to extract text and metadata
    from plain text files.
    """
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text content from a TXT file.
        
        Args:
            file_path: Path to the TXT file.
            
        Returns:
            The extracted text content as a string.
            
        Raises:
            ValueError: If the TXT file cannot be processed.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Failed to extract text from TXT file: {str(e)}")
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a TXT file.
        
        Args:
            file_path: Path to the TXT file.
            
        Returns:
            A dictionary containing metadata about the TXT file.
            
        Raises:
            ValueError: If the TXT file cannot be processed.
        """
        try:
            metadata = {
                "filename": file_path.name,
                "file_size": os.path.getsize(file_path),
                "file_type": FileType.TXT,
                "extracted_at": datetime.now().isoformat(),
            }
            
            # Count lines and characters
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
                lines = content.split('\n')
                
                metadata["line_count"] = len(lines)
                metadata["character_count"] = len(content)
                metadata["word_count"] = len(content.split())
            
            return metadata
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from TXT file: {str(e)}")
    
    @classmethod
    def supports_filetype(cls, file_type: FileType) -> bool:
        """Check if this extractor supports the given file type.
        
        Args:
            file_type: The type of file to check support for.
            
        Returns:
            True if this extractor supports TXT files, False otherwise.
        """
        return file_type == FileType.TXT 