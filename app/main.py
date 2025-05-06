import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as api_v1_router
from app.core.config import API_HOST, API_PORT, get_settings

# Create FastAPI application
app = FastAPI(
    title="Chroma API",
    description="API for processing documents and storing them in a vector database",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_v1_router)

# Add a root endpoint
@app.get("/")
async def root():
    return {
        "name": "Chroma API",
        "version": "1.0.0",
        "description": "API for processing documents and storing them in a vector database",
        "endpoints": {
            "upload": "/api/v1/upload",
            "get_document": "/api/v1/documents/{doc_id}",
            "delete_document": "/api/v1/documents/{doc_id}",
            "search": "/api/v1/search?query={query}&limit={limit}",
        }
    }

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "config": get_settings()}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    status_code = 500
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": str(exc),
            "detail": getattr(exc, "detail", str(exc))
        },
    )

# Run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    ) 