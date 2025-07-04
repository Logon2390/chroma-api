import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# File Processing
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # Default: 10MB
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "250"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Vector Store Settings
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Split by headers
CHUNK_HEADERS = os.getenv("CHUNK_HEADERS", "").split(",")

# Get all config as dictionary
def get_settings() -> Dict[str, Any]:
    return {
        "api": {
            "host": API_HOST,
            "port": API_PORT,
        },
        "files": {
            "upload_dir": str(UPLOAD_DIR),
            "max_size": MAX_FILE_SIZE,
        },
        "vector_store": {
            "db_dir": CHROMA_DB_DIR,
            "embedding_model": EMBEDDING_MODEL,
        },
        "chunk_processing": {
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "headers": CHUNK_HEADERS,
        },
    } 