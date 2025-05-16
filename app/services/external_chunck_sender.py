from fastapi import HTTPException
import httpx
from typing import List, Dict, Any
from app.models.schemas import DocumentChunk

class ExternalChunkSender:
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    async def send_chunks(self, chunks: List[DocumentChunk], metadata: Dict[str, Any]):
        try:
            chunks_dict = [chunk.model_dump() for chunk in chunks]
            payload = {
                "chunks": chunks_dict,
                "metadata": metadata
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=30.0
                )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"External API error: {response.text}"
                )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error connecting to external API: {str(e)}"
            )