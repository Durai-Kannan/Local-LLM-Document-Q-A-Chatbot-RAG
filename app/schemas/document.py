from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DocumentMetadata(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    file_size: int
    file_hash: str
    created_at: str
    total_pages: Optional[int] = 1
    total_chunks: int = 0

class DocumentResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    file_size: int
    created_at: str
    total_chunks: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

class DocumentChunkSchema(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    page: Optional[int] = None
    chunk_index: int
    text: str
    metadata: Dict[str, Any]
