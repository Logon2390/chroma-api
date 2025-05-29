import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models.schemas import DocumentChunk, DocumentMetadata, FileType
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP, CHUNK_HEADERS

class ChunkProcessor:
    
    def split_text_into_chunks(
        self, 
        text: str, 
        metadata: Dict[str, Any], 
        chunk_size: int = CHUNK_SIZE, 
        chunk_overlap: int = CHUNK_OVERLAP
    ) -> List[DocumentChunk]:
        header_keywords = CHUNK_HEADERS
        doc_id = str(uuid.uuid4())
        file_type = self._resolve_file_type(metadata)
        document_metadata = self._create_metadata(metadata, file_type, text, doc_id)

        if header_keywords:
            text_chunks = self._split_by_headers(text, header_keywords)
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            text_chunks = splitter.split_text(text)

        document_chunks = []
        for chunk_text in text_chunks:
            chunk_id = str(uuid.uuid4())
            chunk = DocumentChunk(
                id=chunk_id,
                text=chunk_text.strip(),
                metadata=document_metadata,
                embedding_id=chunk_id
            )
            document_chunks.append(chunk)
            
        return document_chunks
    
    
    def _split_by_headers(self, text: str, headers: List[str]) -> List[str]:
        print("headers:")
        print(headers)
        import re
        escaped_headers = [re.escape(h.strip()) for h in headers]
        pattern = re.compile(rf"^[ \t]*({'|'.join(escaped_headers)})", re.MULTILINE | re.IGNORECASE)

        matches = list(pattern.finditer(text))
        result = []

        if not matches:
            return [text.strip()]

        for i, match in enumerate(matches):
            print(f"Match found: {match.group()}")
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk = text[start:end].strip()
            result.append(chunk)

        return result



    def _resolve_file_type(self, metadata: Dict[str, Any]) -> FileType:
        file_type = metadata.get("file_type")
        if isinstance(file_type, str):
            try:
                return FileType(file_type.lower())
            except ValueError:
                return FileType.TXT
        return file_type if isinstance(file_type, FileType) else FileType.TXT

    def _create_metadata(self, metadata: Dict[str, Any], file_type: FileType, text: str, doc_id: str) -> DocumentMetadata:
        return DocumentMetadata(
            filename=metadata.get("filename", "unknown.txt"),
            file_type=file_type,
            content_length=metadata.get("content_length", len(text)),
            upload_timestamp=metadata.get("upload_timestamp", ""),
            additional_metadata={
                **metadata.get("additional_metadata", {}),
                "parent_doc_id": doc_id
            }
        )
