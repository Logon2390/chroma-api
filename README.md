# AI Vector API

A FastAPI-based API for processing documents (PDF, DOCX, TXT) and storing their content in a vector database (ChromaDB) using LangChain.

## Features

- File upload endpoint for PDF, DOCX, and TXT files
- Text extraction from uploaded documents
- Storage of document content in ChromaDB vector database
- Semantic search capabilities
- Document retrieval and deletion
- SOLID architecture principles
- Extensible design for adding new document types

## Project Structure

```
ai_vector_api/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routes.py         # API endpoints
│   ├── core/
│   │   └── config.py             # Configuration settings
│   ├── services/
│   │   ├── file_processor.py     # File processing service
│   │   ├── extractors/
│   │   │   ├── base.py           # Base extractor interface
│   │   │   ├── pdf_extractor.py  # PDF extraction implementation
│   │   │   ├── docx_extractor.py # DOCX extraction implementation
│   │   │   └── txt_extractor.py  # TXT extraction implementation
│   │   └── vector_store.py       # Vector database service
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   └── main.py                   # FastAPI application
│
├── .env                          # Environment variables
├── requirements.txt              # Project dependencies
└── README.md                     # This file
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-vector-api
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

Create a `.env` file in the root directory with the following settings:

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# File Processing
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Vector Store
CHROMA_DB_DIR=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional AI Provider Keys (if needed)
# OPENAI_API_KEY=your_key_here
```

## Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## Using the API

### Uploading a Document

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"
```

### Searching for Documents

```bash
curl -X GET "http://localhost:8000/api/v1/search?query=your%20search%20query&limit=5" \
  -H "accept: application/json"
```

### Retrieving a Document

```bash
curl -X GET "http://localhost:8000/api/v1/documents/{document_id}" \
  -H "accept: application/json"
```

### Deleting a Document

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/{document_id}" \
  -H "accept: application/json"
```

## Extending the API

### Adding New Document Types

1. Create a new extractor class in `app/services/extractors/`
2. Inherit from `BaseExtractor` and implement its methods
3. Add the new file type to the `FileType` enum in `app/models/schemas.py`
4. Register your new extractor in `FileProcessor.__init__()`