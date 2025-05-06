import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

import PyPDF2

from app.services.extractors.base import BaseExtractor
from app.models.schemas import FileType


class PDFExtractor(BaseExtractor):
    """Extractor for PDF files.
    
    This class provides functionality to extract text and metadata
    from PDF files using PyPDF2.
    """
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            The extracted text content as a string.
            
        Raises:
            ValueError: If the PDF file cannot be processed.
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            A dictionary containing metadata about the PDF file.
            
        Raises:
            ValueError: If the PDF file cannot be processed.
        """
        try:
            metadata = {
                "filename": file_path.name,
                "file_size": os.path.getsize(file_path),
                "file_type": FileType.PDF,
                "extracted_at": datetime.now().isoformat(),
            }
            
            # Extract PDF-specific metadata
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_info = pdf_reader.metadata
                
                if pdf_info:
                    pdf_metadata = {}
                    for key, value in pdf_info.items():
                        if key.startswith('/'):
                            pdf_metadata[key[1:]] = value
                        else:
                            pdf_metadata[key] = value
                    
                    metadata["pdf_metadata"] = pdf_metadata
                
                metadata["page_count"] = len(pdf_reader.pages)
                
            return metadata
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from PDF: {str(e)}")
    
    @classmethod
    def supports_filetype(cls, file_type: FileType) -> bool:
        """Check if this extractor supports the given file type.
        
        Args:
            file_type: The type of file to check support for.
            
        Returns:
            True if this extractor supports PDF files, False otherwise.
        """
        return file_type == FileType.PDF 